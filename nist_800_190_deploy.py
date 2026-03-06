#!/usr/bin/env python3
"""
NIST 800-190 Policy Deployment Script

This script deploys NIST SP 800-190 compliant policies to RHACS/ACS.
It reads connection configuration from .env file and policy definitions 
from nist_800_190_policies.json.

Usage:
    python3 nist_800_190_deploy.py
"""

import json
import requests
import logging
import sys
import os
from typing import Dict, List, Any
from urllib.parse import urljoin
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        logger.info(f"Loaded configuration from {env_file}")
        return env_vars
    except FileNotFoundError:
        logger.error(f"Environment file '{env_file}' not found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading environment file: {e}")
        sys.exit(1)


class RHACSClient:
    """RHACS/ACS API client for managing security policies."""
    
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
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text[:500]}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to RHACS Central."""
        try:
            response = self._make_request('GET', '/v1/metadata')
            metadata = response.json()
            logger.info(f"Successfully connected to RHACS Central (version: {metadata.get('version', 'unknown')})")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RHACS Central: {e}")
            return False
    
    def create_policy(self, policy: Dict[str, Any]) -> tuple[bool, str]:
        """Create a security policy in RHACS."""
        try:
            response = self._make_request('POST', '/v1/policies', policy)
            policy_id = response.json().get('id', 'unknown')
            logger.info(f"✓ Created policy: {policy['name']} (ID: {policy_id})")
            return True, policy_id
        except Exception as e:
            logger.error(f"✗ Failed to create policy {policy['name']}: {e}")
            return False, str(e)
    
    def get_existing_policies(self) -> List[Dict]:
        """Get list of existing policies."""
        try:
            response = self._make_request('GET', '/v1/policies')
            return response.json().get('policies', [])
        except Exception as e:
            logger.error(f"Failed to fetch existing policies: {e}")
            return []


def load_nist_policies(policies_file: str = "nist_800_190_policies.json") -> List[Dict[str, Any]]:
    """Load NIST 800-190 policies from JSON file."""
    try:
        with open(policies_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        policies = data.get('nist_800_190_policies', [])
        logger.info(f"Loaded {len(policies)} policies from {policies_file}")
        return policies
        
    except FileNotFoundError:
        logger.error(f"Policy file '{policies_file}' not found")
        logger.error("Please run nist_800_190_generate.py first to generate the policies")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in policy file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading policy file: {e}")
        sys.exit(1)


def print_summary(total: int, created: int, skipped: int, failed: int):
    """Print deployment summary."""
    logger.info("=" * 80)
    logger.info("NIST 800-190 POLICY DEPLOYMENT SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total policies processed: {total}")
    logger.info(f"Successfully created: {created}")
    logger.info(f"Skipped (already exist): {skipped}")
    logger.info(f"Failed to create: {failed}")
    logger.info("=" * 80)
    
    if failed > 0:
        logger.warning(f"{failed} policies failed to create. Check logs for details.")
    else:
        logger.info("All NIST 800-190 policies deployed successfully!")


def main():
    """Main function to deploy NIST 800-190 policies to RHACS."""
    logger.info("=" * 80)
    logger.info("NIST SP 800-190 Policy Deployment")
    logger.info("Application Container Security Guide")
    logger.info("=" * 80)
    logger.info("")
    
    # Load environment variables
    env_vars = load_env_file()
    
    rhacs_url = env_vars.get('RHACS_URL')
    rhacs_token = env_vars.get('RHACS_TOKEN')
    
    if not rhacs_url or not rhacs_token:
        logger.error("RHACS_URL and RHACS_TOKEN must be set in .env file")
        sys.exit(1)
    
    logger.info(f"RHACS URL: {rhacs_url}")
    logger.info("")
    
    # Initialize RHACS client
    client = RHACSClient(rhacs_url, rhacs_token)
    
    # Test connection
    if not client.test_connection():
        logger.error("Failed to connect to RHACS. Please check your credentials.")
        sys.exit(1)
    
    logger.info("")
    
    # Get existing policies to avoid duplicates
    existing_policies = client.get_existing_policies()
    existing_policy_names = {policy.get('name', '') for policy in existing_policies}
    logger.info(f"Found {len(existing_policies)} existing policies in RHACS")
    logger.info("")
    
    # Load NIST 800-190 policies
    policies = load_nist_policies()
    
    # Deploy policies
    logger.info("Starting policy deployment...")
    logger.info("-" * 80)
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    for policy in policies:
        policy_name = policy['name']
        
        # Skip if policy already exists
        if policy_name in existing_policy_names:
            logger.info(f"⊗ Policy already exists, skipping: {policy_name}")
            skipped_count += 1
            continue
        
        # Create the policy
        success, result = client.create_policy(policy)
        if success:
            created_count += 1
        else:
            failed_count += 1
    
    logger.info("")
    
    # Print summary
    print_summary(len(policies), created_count, skipped_count, failed_count)
    
    if failed_count > 0:
        sys.exit(1)
    else:
        logger.info("")
        logger.info("Next Steps:")
        logger.info("  1. View policies in RHACS UI: Platform Configuration → Policy Management")
        logger.info("  2. Filter by 'NIST 800-190' to see the deployed policies")
        logger.info("  3. Configure enforcement actions and notifiers as needed")
        logger.info("  4. Add exclusions for system namespaces if required")
        logger.info("")
        sys.exit(0)


if __name__ == "__main__":
    main()
