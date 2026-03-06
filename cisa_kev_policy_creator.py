import os
import json
import logging
import requests
import schedule
import time
from typing import Dict, Any, List

# --- RHACS Client (from existing script) ---
class RHACSClient:
    def __init__(self, central_url: str, api_token: str):
        self.central_url = central_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = False  # Consider using proper certificate validation in production

    def get_existing_policies(self) -> List[str]:
        """Fetches the names of all existing policies in RHACS."""
        url = f"{self.central_url}/v1/policies"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return [policy['name'] for policy in response.json().get('policies', [])]
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get existing policies: {e}")
            return []

    def create_policy(self, policy: Dict[str, Any]) -> bool:
        """Creates a single policy in RHACS."""
        url = f"{self.central_url}/v1/policies"
        try:
            response = self.session.post(url, json=policy)
            if response.status_code == 200:
                logging.info(f"Successfully created policy: {policy.get('name')}")
                return True
            elif response.status_code == 409 or "already exists" in response.text:
                 logging.warning(f"Policy '{policy.get('name')}' already exists in RHACS.")
                 return False
            else:
                logging.error(f"Failed to create policy '{policy.get('name')}'. Status: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Exception while creating policy '{policy.get('name')}': {e}")
            return False

# --- CISA KEV Client ---
class CisaKevClient:
    def __init__(self):
        self.url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        self.session = requests.Session()

    def get_known_exploited_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Fetches the CISA Known Exploited Vulnerabilities (KEV) catalog."""
        logging.info("Fetching vulnerabilities from the CISA KEV catalog.")
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            data = response.json()
            logging.info(f"Found {data.get('count', 0)} total vulnerabilities in the CISA KEV catalog.")
            return data.get('vulnerabilities', [])
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch vulnerabilities from CISA KEV catalog: {e}")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from CISA KEV response: {e}")
            return []

# --- Policy Transformer ---
class PolicyTransformer:
    def from_kev_to_rhacs(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Transforms a CISA KEV entry into a RHACS policy format."""
        cve_id = vulnerability.get("cveID")
        if not cve_id:
            logging.warning("Skipping vulnerability without a CVE ID.")
            return None

        policy = {
            "name": f"CISA KEV: {vulnerability.get('vulnerabilityName', cve_id)}",
            "description": f"Policy for a known exploited vulnerability listed in the CISA KEV catalog. More details: {vulnerability.get('notes', 'N/A')}",
            "rationale": f"This vulnerability ({cve_id}) is listed by CISA as actively exploited in the wild. Remediation is strongly advised.",
            "remediation": f"Required Action: {vulnerability.get('requiredAction', 'Refer to vendor for patching details.')}",
            "severity": "CRITICAL_SEVERITY",
            "lifecycleStages": ["DEPLOY"],
            "categories": ["Vulnerability Management", "Threat Intelligence"],
            "policySections": [
                {
                    "sectionName": "Vulnerabilities",
                    "policyGroups": [
                        {
                            "fieldName": "CVE",
                            "booleanOperator": "OR",
                            "negate": False,
                            "values": [{"value": cve_id}]
                        }
                    ]
                }
            ],
            "exclusions": [],
            "enforcementActions": ["FAIL_DEPLOYMENT"],
            "notifiers": []
        }
        return policy

# --- Main Application Logic ---
def load_configuration(config_file: str = "config.json") -> Dict[str, Any]:
    """Loads configuration from a JSON file."""
    if not os.path.exists(config_file):
        logging.critical(f"Configuration file '{config_file}' not found. Please create it from the template.")
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    log_level = config.get('logging', {}).get('level', 'INFO').upper()
    log_format = config.get('logging', {}).get('format', '%(asctime)s - %(levelname)s - %(message)s')
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=log_level, format=log_format)
    
    return config

def filter_vulnerabilities(vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters vulnerabilities based on keywords relevant to containerized environments."""
    keywords = [
        "kubernetes", "openshift", "container", "docker", "crio", "containerd",
        "runc", "etcd", "flannel", "calico", "istio", "envoy", "helm", "tiller",
        "kubelet", "api server", "scheduler", "controller manager"
    ]
    
    filtered_vulns = []
    for vuln in vulnerabilities:
        search_text = (
            vuln.get("vulnerabilityName", "") + 
            vuln.get("shortDescription", "") + 
            vuln.get("requiredAction", "")
        ).lower()
        
        if any(keyword in search_text for keyword in keywords):
            filtered_vulns.append(vuln)
            
    logging.info(f"Filtered down to {len(filtered_vulns)} vulnerabilities relevant to container technologies.")
    return filtered_vulns

def run_policy_creation_job():
    """The main job to be scheduled."""
    logging.info("Running the daily CISA KEV policy creation job...")
    try:
        config = load_configuration()
    except FileNotFoundError:
        return

    rhacs_config = config.get('rhacs', {})
    central_url = rhacs_config.get('central_url')
    api_token = rhacs_config.get('api_token')

    if not all([central_url, api_token]):
        logging.critical("Missing required configuration for RHACS. Skipping job.")
        return

    rhacs_client = RHACSClient(central_url, api_token)
    kev_client = CisaKevClient()
    transformer = PolicyTransformer()
    
    existing_policy_names = rhacs_client.get_existing_policies()
    
    vulnerabilities = kev_client.get_known_exploited_vulnerabilities()
    
    if not vulnerabilities:
        logging.info("No vulnerabilities found from CISA KEV catalog. Job finished.")
        return

    filtered_vulnerabilities = filter_vulnerabilities(vulnerabilities)

    if not filtered_vulnerabilities:
        logging.info("No relevant container-focused vulnerabilities found in the CISA KEV catalog at this time. Job finished.")
        return

    created_count = 0
    for vuln in filtered_vulnerabilities:
        rhacs_policy = transformer.from_kev_to_rhacs(vuln)
        
        if not rhacs_policy:
            continue

        if rhacs_policy['name'] in existing_policy_names:
            logging.info(f"Skipping policy '{rhacs_policy['name']}' as it already exists.")
            continue
            
        if rhacs_client.create_policy(rhacs_policy):
            created_count += 1

    logging.info(f"Policy creation job finished. Created {created_count} new policies.")


def main():
    """Main function to run the CISA KEV to RHACS policy creator as a daily agent."""
    
    # Run the job once at startup
    run_policy_creation_job()
    
    # Schedule the job to run every 24 hours
    schedule.every(24).hours.do(run_policy_creation_job)
    
    logging.info("Scheduler started. The policy creation job will run every 24 hours.")
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Check for pending jobs every 60 seconds

if __name__ == "__main__":
    main()
