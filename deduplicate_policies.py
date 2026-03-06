import os
import json
import logging
import requests
from typing import Dict, Any, List, Tuple
from dateutil import parser

# --- RHACS Client ---
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

    def get_all_policies(self) -> List[Dict[str, Any]]:
        """Fetches all policies from RHACS."""
        url = f"{self.central_url}/v1/policies"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json().get('policies', [])
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get policies: {e}")
            return []

    def delete_policy(self, policy_id: str) -> bool:
        """Deletes a single policy by its ID."""
        url = f"{self.central_url}/v1/policies/{policy_id}"
        try:
            response = self.session.delete(url)
            if response.status_code == 204:
                logging.info(f"Successfully deleted policy with ID: {policy_id}")
                return True
            else:
                logging.error(f"Failed to delete policy {policy_id}. Status: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Exception while deleting policy {policy_id}: {e}")
            return False

# --- Deduplication Logic ---
class PolicyDeduplicator:
    def find_and_remove_duplicates(self, client: RHACSClient):
        """Finds and removes duplicate policies based on CVEs."""
        logging.info("Starting policy deduplication process...")
        all_policies = client.get_all_policies()

        if not all_policies:
            logging.info("No policies found to deduplicate.")
            return

        # Group policies by the CVEs they contain
        cve_to_policies: Dict[str, List[Dict[str, Any]]] = {}
        for policy in all_policies:
            cves = self._extract_cves(policy)
            if not cves:
                continue
            
            # Use a tuple of sorted CVEs as the key to handle policies with multiple CVEs
            cve_key = tuple(sorted(cves))
            if cve_key not in cve_to_policies:
                cve_to_policies[cve_key] = []
            cve_to_policies[cve_key].append(policy)

        # Identify and remove duplicates
        total_deleted = 0
        for cve_key, policies in cve_to_policies.items():
            if len(policies) > 1:
                logging.warning(f"Found {len(policies)} duplicate policies for CVE(s): {', '.join(cve_key)}")
                
                # Sort policies by creation time (newest first)
                policies.sort(key=lambda p: parser.parse(p.get('createdAt', '1970-01-01T00:00:00Z')), reverse=True)
                
                # Keep the newest one, delete the rest
                policy_to_keep = policies[0]
                logging.info(f"Keeping the newest policy: '{policy_to_keep['name']}' (ID: {policy_to_keep['id']})")
                
                for policy_to_delete in policies[1:]:
                    logging.info(f"Deleting older policy: '{policy_to_delete['name']}' (ID: {policy_to_delete['id']})")
                    if client.delete_policy(policy_to_delete['id']):
                        total_deleted += 1
        
        logging.info(f"Deduplication process finished. Deleted {total_deleted} duplicate policies.")

    def _extract_cves(self, policy: Dict[str, Any]) -> List[str]:
        """Extracts all CVEs from a policy's definition."""
        cves = set()
        for section in policy.get("policySections", []):
            for group in section.get("policyGroups", []):
                if group.get("fieldName") == "CVE":
                    for value in group.get("values", []):
                        if value.get("value"):
                            cves.add(value["value"])
        return list(cves)

# --- Main ---
def load_configuration(config_file: str = "config.json") -> Dict[str, Any]:
    """Loads configuration from a JSON file."""
    if not os.path.exists(config_file):
        logging.critical(f"Configuration file '{config_file}' not found.")
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    log_level = config.get('logging', {}).get('level', 'INFO').upper()
    log_format = config.get('logging', {}).get('format', '%(asctime)s - %(levelname)s - %(message)s')
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=log_level, format=log_format)
    
    return config

def main():
    """Main function to run the deduplication script."""
    try:
        config = load_configuration()
    except FileNotFoundError:
        return

    rhacs_config = config.get('rhacs', {})
    central_url = rhacs_config.get('central_url')
    api_token = rhacs_config.get('api_token')

    if not all([central_url, api_token]):
        logging.critical("Missing required configuration for RHACS.")
        return

    rhacs_client = RHACSClient(central_url, api_token)
    deduplicator = PolicyDeduplicator()
    deduplicator.find_and_remove_duplicates(rhacs_client)

if __name__ == "__main__":
    main()
