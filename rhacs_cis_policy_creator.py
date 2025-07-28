#!/usr/bin/env python3
"""
RHACS CIS Policy Creator

This script connects to Red Hat Advanced Cluster Security (RHACS) and creates
security policies based on CIS benchmarks for both Kubernetes and Docker.
"""

import json
import requests
import logging
import sys
import os
from typing import Dict, List, Any
from urllib.parse import urljoin
import urllib3

# Disable SSL warnings for demo environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global logger (will be configured after loading config)
logger = logging.getLogger(__name__)


def load_configuration(config_file: str = "config.json") -> Dict[str, Any]:
    """Load application configuration from JSON file."""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_file)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Setup logging based on configuration
        log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
        log_format = config.get('logging', {}).get('format', '%(asctime)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            force=True  # Override any existing configuration
        )
        
        logger.info(f"Successfully loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{config_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        sys.exit(1)


class RHACSClient:
    """RHACS API client for managing security policies."""
    
    def __init__(self, central_url: str, api_token: str):
        self.central_url = central_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> requests.Response:
        """Make HTTP request to RHACS API."""
        url = urljoin(self.central_url, endpoint)
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                verify=False  # For demo environments
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to RHACS Central."""
        try:
            response = self._make_request('GET', '/v1/metadata')
            logger.info("Successfully connected to RHACS Central")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RHACS Central: {e}")
            return False
    
    def create_policy(self, policy: Dict[str, Any]) -> bool:
        """Create a security policy in RHACS."""
        try:
            response = self._make_request('POST', '/v1/policies', policy)
            policy_id = response.json().get('id', 'unknown')
            logger.info(f"Successfully created policy: {policy['name']} (ID: {policy_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to create policy {policy['name']}: {e}")
            return False
    
    def get_existing_policies(self) -> List[Dict]:
        """Get list of existing policies."""
        try:
            response = self._make_request('GET', '/v1/policies')
            return response.json().get('policies', [])
        except Exception as e:
            logger.error(f"Failed to fetch existing policies: {e}")
            return []


class CISPolicyGenerator:
    """Generator for CIS benchmark-based security policies."""
    
    def __init__(self, policies_config_file: str = "cis_policies.json"):
        """Initialize the generator with a policies configuration file path."""
        self.config_file = policies_config_file
        self._policies_data = None
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from the JSON configuration file."""
        if self._policies_data is None:
            try:
                # Get the directory where the script is located
                script_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(script_dir, self.config_file)
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._policies_data = json.load(f)
                logger.info(f"Successfully loaded policy configurations from {config_path}")
            except FileNotFoundError:
                logger.error(f"Policy configuration file '{self.config_file}' not found")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in policy configuration file: {e}")
                raise
            except Exception as e:
                logger.error(f"Error loading policy configuration file: {e}")
                raise
        
        return self._policies_data
    
    def get_kubernetes_cis_policies(self) -> List[Dict[str, Any]]:
        """Load Kubernetes CIS benchmark policies from configuration file."""
        policies_data = self._load_policies()
        return policies_data.get('kubernetes_policies', [])
    
    def get_docker_cis_policies(self) -> List[Dict[str, Any]]:
        """Load Docker CIS benchmark policies from configuration file."""
        policies_data = self._load_policies()
        return policies_data.get('docker_policies', [])
    
    def get_runtime_cis_policies(self) -> List[Dict[str, Any]]:
        """Load Runtime CIS benchmark policies from configuration file."""
        policies_data = self._load_policies()
        return policies_data.get('runtime_policies', [])


def main():
    """Main function to create CIS benchmark policies in RHACS."""
    # Load configuration first
    config = load_configuration()
    
    logger.info("Starting RHACS CIS Policy Creator")
    
    # Get RHACS connection parameters from config
    rhacs_config = config.get('rhacs', {})
    central_url = rhacs_config.get('central_url')
    api_token = rhacs_config.get('api_token')
    
    if not central_url or not api_token:
        logger.error("RHACS central_url and api_token must be provided in config.json")
        sys.exit(1)
    
    # Initialize RHACS client
    client = RHACSClient(central_url, api_token)
    
    # Test connection
    if not client.test_connection():
        logger.error("Failed to connect to RHACS. Exiting.")
        sys.exit(1)
    
    # Get existing policies to avoid duplicates
    existing_policies = client.get_existing_policies()
    existing_policy_names = {policy.get('name', '') for policy in existing_policies}
    
    # Generate CIS policies
    try:
        policies_config = config.get('policies', {})
        policies_config_file = policies_config.get('config_file', 'cis_policies.json')
        skip_existing = policies_config.get('skip_existing', True)
        
        generator = CISPolicyGenerator(policies_config_file)
        
        # Get Kubernetes CIS policies
        k8s_policies = generator.get_kubernetes_cis_policies()
        logger.info(f"Loaded {len(k8s_policies)} Kubernetes CIS policies")
        
        # Get Docker CIS policies
        docker_policies = generator.get_docker_cis_policies()
        logger.info(f"Loaded {len(docker_policies)} Docker CIS policies")
        
        # Get Runtime CIS policies
        runtime_policies = generator.get_runtime_cis_policies()
        logger.info(f"Loaded {len(runtime_policies)} Runtime CIS policies")
    except Exception as e:
        logger.error(f"Failed to load policy configurations: {e}")
        sys.exit(1)
    
    # Combine all policies
    all_policies = k8s_policies + docker_policies + runtime_policies
    
    # Create policies
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    for policy in all_policies:
        policy_name = policy['name']
        
        # Skip if policy already exists and skip_existing is enabled
        if skip_existing and policy_name in existing_policy_names:
            logger.info(f"Policy '{policy_name}' already exists, skipping")
            skipped_count += 1
            continue
        
        # Create the policy
        if client.create_policy(policy):
            created_count += 1
        else:
            failed_count += 1
    
    # Summary
    logger.info("=" * 50)
    logger.info("RHACS CIS Policy Creation Summary")
    logger.info("=" * 50)
    logger.info(f"Total policies processed: {len(all_policies)}")
    logger.info(f"Successfully created: {created_count}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Failed to create: {failed_count}")
    logger.info("=" * 50)
    
    if failed_count > 0:
        logger.warning(f"{failed_count} policies failed to create. Check logs for details.")
        sys.exit(1)
    else:
        logger.info("All policies processed successfully!")


if __name__ == "__main__":
    main() 