#!/usr/bin/env python3
"""
Post-Quantum Cryptography (PQC) Policy Creator for RHACS
Creates and manages PQC enforcement policies in Red Hat Advanced Cluster Security

This script creates policies to:
1. Enforce quantum-resistant cryptographic algorithms
2. Detect deprecated crypto vulnerable to quantum attacks
3. Ensure PQC-ready libraries and configurations
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List

# Disable SSL warnings for demo environments
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RHACSClient:
    """Client for interacting with RHACS API"""
    
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

    def get_existing_policies(self) -> List[Dict[str, Any]]:
        """Fetches existing policies from RHACS"""
        url = f"{self.central_url}/v1/policies"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json().get('policies', [])
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get existing policies: {e}")
            return []

    def create_policy(self, policy: Dict[str, Any]) -> bool:
        """Creates a single policy in RHACS"""
        url = f"{self.central_url}/v1/policies"
        try:
            response = self.session.post(url, json=policy)
            if response.status_code == 200:
                policy_data = response.json()
                logging.info(f"✅ Successfully created policy: {policy['name']} (ID: {policy_data.get('id', 'Unknown')})")
                return True
            else:
                logging.error(f"❌ Failed to create policy: {policy['name']}")
                logging.error(f"   Status Code: {response.status_code}")
                logging.error(f"   Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Exception while creating policy {policy['name']}: {e}")
            return False

class PQCPolicyGenerator:
    """Generates and manages Post-Quantum Cryptography policies"""
    
    def __init__(self, policy_file: str = "working_pqc_policies.json"):
        self.policy_file = policy_file
        self.policies = self._load_policies()

    def _load_policies(self) -> List[Dict[str, Any]]:
        """Loads PQC policies from JSON file"""
        if not os.path.exists(self.policy_file):
            logging.error(f"Policy file '{self.policy_file}' not found.")
            return []
        
        try:
            with open(self.policy_file, 'r') as f:
                data = json.load(f)
                return data.get('pqc_policies', [])
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing policy file: {e}")
            return []
        except Exception as e:
            logging.error(f"Error loading policy file: {e}")
            return []

    def create_all_policies(self, client: RHACSClient, skip_existing: bool = True) -> None:
        """Creates all PQC policies in RHACS"""
        if not self.policies:
            logging.warning("No PQC policies found to create.")
            return

        existing_policies = []
        if skip_existing:
            existing_policies = client.get_existing_policies()
            existing_names = {policy['name'] for policy in existing_policies}

        created_count = 0
        skipped_count = 0
        failed_count = 0

        logging.info(f"📋 Processing {len(self.policies)} PQC policies...")
        
        for policy in self.policies:
            policy_name = policy['name']
            
            if skip_existing and policy_name in existing_names:
                logging.info(f"⏭️  Skipping existing policy: {policy_name}")
                skipped_count += 1
                continue
            
            logging.info(f"🔐 Creating PQC policy: {policy_name}")
            if client.create_policy(policy):
                created_count += 1
            else:
                failed_count += 1

        # Summary
        logging.info(f"\n📊 PQC Policy Creation Summary:")
        logging.info(f"   ✅ Created: {created_count}")
        logging.info(f"   ⏭️  Skipped: {skipped_count}")
        logging.info(f"   ❌ Failed: {failed_count}")
        logging.info(f"   📋 Total: {len(self.policies)}")

def load_configuration(config_file: str = "config.json") -> Dict[str, Any]:
    """Loads configuration from JSON file"""
    if not os.path.exists(config_file):
        logging.critical(f"Configuration file '{config_file}' not found.")
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Setup logging
    log_level = config.get('logging', {}).get('level', 'INFO').upper()
    log_format = config.get('logging', {}).get('format', '%(asctime)s - %(levelname)s - %(message)s')
    
    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=log_level, format=log_format)
    
    return config

def main():
    """Main function to create PQC policies"""
    try:
        # Load configuration
        config = load_configuration()
    except FileNotFoundError:
        print("❌ Configuration file not found. Please ensure config.json exists.")
        return

    # Extract RHACS configuration
    rhacs_config = config.get('rhacs', {})
    central_url = rhacs_config.get('central_url')
    api_token = rhacs_config.get('api_token')

    if not all([central_url, api_token]):
        logging.critical("❌ Missing required RHACS configuration (central_url, api_token).")
        return

    # Extract policy configuration
    policy_config = config.get('policies', {})
    skip_existing = policy_config.get('skip_existing', True)

    logging.info("🚀 Starting Post-Quantum Cryptography Policy Creation")
    logging.info(f"   🎯 RHACS URL: {central_url}")
    logging.info(f"   ⏭️  Skip Existing: {skip_existing}")

    # Initialize clients
    rhacs_client = RHACSClient(central_url, api_token)
    pqc_generator = PQCPolicyGenerator()

    # Create policies
    pqc_generator.create_all_policies(rhacs_client, skip_existing)

    logging.info("🏁 Post-Quantum Cryptography policy creation completed!")

if __name__ == "__main__":
    main()