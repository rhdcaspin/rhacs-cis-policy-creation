#!/usr/bin/env python3
"""
RHACS Data Sovereignty Policy Creator

This script connects to Red Hat Advanced Cluster Security (RHACS) and creates
security policies specifically designed to enforce data sovereignty and geographic
data residency requirements.

Data sovereignty policies help ensure compliance with regulations such as:
- GDPR (General Data Protection Regulation) - EU
- CCPA (California Consumer Privacy Act) - US
- LGPD (Lei Geral de Proteção de Dados) - Brazil
- PIPEDA (Personal Information Protection and Electronic Documents Act) - Canada
- And other regional data protection regulations
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

# Global logger
logger = logging.getLogger(__name__)


def load_configuration(config_file: str = "config.json") -> Dict[str, Any]:
    """Load application configuration from JSON file."""
    try:
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
            force=True
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
                verify=False
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


class DataSovereigntyPolicyGenerator:
    """Generator for data sovereignty security policies."""
    
    def __init__(self, policies_file: str = "data_sovereignty_policies.json"):
        """Initialize the generator with a policies configuration file path."""
        self.policies_file = policies_file
        self._policies_data = None
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from the JSON configuration file."""
        if self._policies_data is None:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(script_dir, self.policies_file)
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._policies_data = json.load(f)
                logger.info(f"Successfully loaded policy configurations from {config_path}")
            except FileNotFoundError:
                logger.error(f"Policy configuration file '{self.policies_file}' not found")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in policy configuration file: {e}")
                raise
            except Exception as e:
                logger.error(f"Error loading policy configuration file: {e}")
                raise
        
        return self._policies_data
    
    def get_data_sovereignty_policies(self) -> List[Dict[str, Any]]:
        """Load data sovereignty policies from configuration file."""
        policies_data = self._load_policies()
        return policies_data.get('data_sovereignty_policies', [])
    
    def get_policies_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get policies filtered by region (e.g., 'EU', 'US')."""
        all_policies = self.get_data_sovereignty_policies()
        region_upper = region.upper()
        return [
            policy for policy in all_policies
            if region_upper in policy.get('name', '').upper() or
               region_upper in policy.get('description', '').upper()
        ]
    
    def get_policies_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get policies filtered by severity level."""
        all_policies = self.get_data_sovereignty_policies()
        severity_upper = severity.upper()
        if not severity_upper.endswith('_SEVERITY'):
            severity_upper += '_SEVERITY'
        return [
            policy for policy in all_policies
            if policy.get('severity', '') == severity_upper
        ]


def print_policy_summary(policies: List[Dict[str, Any]]):
    """Print a summary of policies to be created."""
    logger.info("=" * 80)
    logger.info("DATA SOVEREIGNTY POLICIES SUMMARY")
    logger.info("=" * 80)
    
    by_severity = {}
    by_lifecycle = {}
    
    for policy in policies:
        severity = policy.get('severity', 'UNKNOWN')
        by_severity[severity] = by_severity.get(severity, 0) + 1
        
        for stage in policy.get('lifecycleStages', []):
            by_lifecycle[stage] = by_lifecycle.get(stage, 0) + 1
    
    logger.info(f"\nTotal policies: {len(policies)}")
    
    logger.info("\nBy Severity:")
    for severity, count in sorted(by_severity.items()):
        logger.info(f"  {severity}: {count}")
    
    logger.info("\nBy Lifecycle Stage:")
    for stage, count in sorted(by_lifecycle.items()):
        logger.info(f"  {stage}: {count}")
    
    logger.info("\nPolicy List:")
    for i, policy in enumerate(policies, 1):
        logger.info(f"  {i}. {policy['name']} [{policy.get('severity', 'N/A')}]")
    
    logger.info("=" * 80)


def main():
    """Main function to create data sovereignty policies in RHACS."""
    # Load configuration first
    config = load_configuration()
    
    logger.info("Starting RHACS Data Sovereignty Policy Creator")
    
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
    
    # Load data sovereignty policies
    try:
        policies_config = config.get('policies', {})
        skip_existing = policies_config.get('skip_existing', True)
        
        generator = DataSovereigntyPolicyGenerator()
        data_sovereignty_policies = generator.get_data_sovereignty_policies()
        
        logger.info(f"Loaded {len(data_sovereignty_policies)} Data Sovereignty policies")
        
        # Print summary
        print_policy_summary(data_sovereignty_policies)
        
    except Exception as e:
        logger.error(f"Failed to load policy configurations: {e}")
        sys.exit(1)
    
    # Create policies
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    logger.info("\nStarting policy creation...")
    
    for policy in data_sovereignty_policies:
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
    
    # Final Summary
    logger.info("=" * 80)
    logger.info("DATA SOVEREIGNTY POLICY CREATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total policies processed: {len(data_sovereignty_policies)}")
    logger.info(f"Successfully created: {created_count}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Failed to create: {failed_count}")
    logger.info("=" * 80)
    
    if failed_count > 0:
        logger.warning(f"{failed_count} policies failed to create. Check logs for details.")
        sys.exit(1)
    else:
        logger.info("All data sovereignty policies processed successfully!")
        logger.info("\nIMPORTANT NOTES:")
        logger.info("1. Review and customize region-specific values in policies")
        logger.info("2. Update node labels to match your cluster topology")
        logger.info("3. Configure data classification labels for your workloads")
        logger.info("4. Test policies in non-production environments first")
        logger.info("5. Some policies require specific annotations/labels to be effective")


if __name__ == "__main__":
    main()

