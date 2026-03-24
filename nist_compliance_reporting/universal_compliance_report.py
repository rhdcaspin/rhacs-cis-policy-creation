#!/usr/bin/env python3
"""
Universal Compliance Reporting Tool for RHACS

This script generates compliance reports for any compliance framework supported by RHACS.
Supports NIST 800-190, NIST 800-53, PCI-DSS, HIPAA, CIS, GDPR, SOC 2, ISO 27001, FedRAMP, and custom frameworks.
"""

import requests
import json
import os
import sys
import yaml
import argparse
from collections import defaultdict
from datetime import datetime
import urllib3

# Disable SSL warnings for demo environment
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# RHACS Configuration from environment variables
RHACS_URL = os.getenv('RHACS_URL')
API_TOKEN = os.getenv('RHACS_API_TOKEN')
VERIFY_SSL = os.getenv('RHACS_VERIFY_SSL', 'false').lower() == 'true'

# Validate required environment variables
if not RHACS_URL:
    print("ERROR: RHACS_URL environment variable not set")
    print("Please set: export RHACS_URL='https://your-rhacs-instance.com'")
    sys.exit(1)

if not API_TOKEN:
    print("ERROR: RHACS_API_TOKEN environment variable not set")
    print("Please set: export RHACS_API_TOKEN='your-api-token'")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def load_frameworks(config_file='compliance_frameworks.yaml'):
    """Load compliance framework definitions"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('frameworks', {})
    except FileNotFoundError:
        print(f"ERROR: Framework configuration file not found: {config_file}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in configuration file: {e}")
        sys.exit(1)

def api_request(endpoint, params=None):
    """Make API request to RHACS"""
    url = f"{RHACS_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params, verify=VERIFY_SSL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request to {endpoint}: {e}")
        return None

def get_policies_for_framework(framework_config):
    """Fetch policies that match the framework criteria"""
    filter_type = framework_config['policy_filter']['type']
    filter_value = framework_config['policy_filter']['value']

    if filter_type == 'category':
        # Search by category
        data = api_request("/v1/policies", params={"query": f"Category:{filter_value}"})
    elif filter_type == 'name_prefix':
        # Search by name prefix
        data = api_request("/v1/policies", params={"query": f"Policy:{filter_value}"})
    elif filter_type == 'name_contains':
        # Search by name contains
        data = api_request("/v1/policies")
    elif filter_type == 'tag':
        # Search by tag
        data = api_request("/v1/policies", params={"query": f"Tag:{filter_value}"})
    else:
        print(f"ERROR: Unknown filter type: {filter_type}")
        return []

    if not data or 'policies' not in data:
        print(f"No policies found for framework")
        return []

    policies = data['policies']

    # Additional filtering for name_contains
    if filter_type == 'name_contains':
        policies = [p for p in policies if filter_value in p.get('name', '')]
    elif filter_type == 'name_prefix':
        policies = [p for p in policies if filter_value in p.get('name', '')]

    return policies

def get_policy_violations(policy_id):
    """Fetch violations for a specific policy"""
    data = api_request(f"/v1/alerts", params={"query": f"Policy Id:{policy_id}"})
    if not data or 'alerts' not in data:
        return []
    return data['alerts']

def get_all_deployments():
    """Fetch all deployments from RHACS"""
    data = api_request("/v1/deployments")
    if not data or 'deployments' not in data:
        print("No deployments found")
        return []
    deployments = data['deployments']
    return deployments

def generate_compliance_report(framework_id, frameworks):
    """Generate compliance report for a specific framework"""

    if framework_id not in frameworks:
        print(f"ERROR: Unknown framework: {framework_id}")
        print(f"Available frameworks: {', '.join(frameworks.keys())}")
        sys.exit(1)

    framework = frameworks[framework_id]
    framework_name = framework['name']

    print("\n" + "="*80)
    print(f"RHACS Compliance Report - {framework_name}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Get policies for this framework
    print(f"Fetching {framework_name} policies...")
    policies = get_policies_for_framework(framework)

    if not policies:
        print(f"No policies found for {framework_name}!")
        print(f"Filter type: {framework['policy_filter']['type']}")
        print(f"Filter value: {framework['policy_filter']['value']}")
        return

    print(f"Found {len(policies)} {framework_name} policies")

    # Get all deployments
    deployments = get_all_deployments()
    print(f"Found {len(deployments)} deployments")

    # Create structure: cluster -> namespace -> deployment -> policy results
    compliance_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    # Track which policies have violations
    policies_with_violations = defaultdict(set)

    print(f"\nAnalyzing policy violations for {framework_name}...")
    # For each policy, get violations and map to deployments
    for policy in policies:
        policy_id = policy['id']
        policy_name = policy['name']
        print(f"  Checking policy: {policy_name}")

        violations = get_policy_violations(policy_id)

        # Track deployments with violations for this policy
        for violation in violations:
            deployment_info = violation.get('deployment', {})
            deployment_id = deployment_info.get('id')
            deployment_name = deployment_info.get('name')
            namespace = deployment_info.get('namespace')
            cluster_name = deployment_info.get('clusterName', 'Unknown')

            if deployment_id:
                policies_with_violations[deployment_id].add(policy_id)

    # Build compliance report for all deployments
    for deployment in deployments:
        deployment_id = deployment.get('id')
        deployment_name = deployment.get('name')
        namespace = deployment.get('namespace')
        cluster_name = deployment.get('clusterName', 'Unknown')

        # Check each policy against this deployment
        for policy in policies:
            policy_id = policy['id']
            policy_name = policy['name']

            # Check if this deployment has violations for this policy
            has_violation = policy_id in policies_with_violations.get(deployment_id, set())

            compliance_data[cluster_name][namespace][deployment_name][policy_name] = {
                'status': 'FAIL' if has_violation else 'PASS',
                'policy_id': policy_id
            }

    # Print the report
    print("\n" + "="*80)
    print(f"COMPLIANCE REPORT BY CLUSTER/NAMESPACE/DEPLOYMENT - {framework_name}")
    print("="*80 + "\n")

    for cluster in sorted(compliance_data.keys()):
        print(f"\n{'#'*80}")
        print(f"CLUSTER: {cluster}")
        print(f"{'#'*80}\n")

        for namespace in sorted(compliance_data[cluster].keys()):
            print(f"\n  Namespace: {namespace}")
            print(f"  {'-'*76}\n")

            for deployment in sorted(compliance_data[cluster][namespace].keys()):
                print(f"    Deployment: {deployment}")

                policy_results = compliance_data[cluster][namespace][deployment]

                # Count pass/fail
                total_policies = len(policy_results)
                failed_policies = sum(1 for r in policy_results.values() if r['status'] == 'FAIL')
                passed_policies = total_policies - failed_policies

                print(f"      Summary: {passed_policies}/{total_policies} policies PASS, {failed_policies}/{total_policies} policies FAIL")
                print()

                # Show failed policies
                if failed_policies > 0:
                    print(f"      Failed Policies:")
                    for policy_name, result in sorted(policy_results.items()):
                        if result['status'] == 'FAIL':
                            print(f"        ❌ {policy_name}")
                    print()

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80 + "\n")

    total_clusters = len(compliance_data)
    total_namespaces = sum(len(namespaces) for namespaces in compliance_data.values())
    total_deployments = sum(
        len(deployments)
        for cluster in compliance_data.values()
        for deployments in cluster.values()
    )

    print(f"Framework:         {framework_name}")
    print(f"Total Clusters:    {total_clusters}")
    print(f"Total Namespaces:  {total_namespaces}")
    print(f"Total Deployments: {total_deployments}")
    print(f"Total Policies:    {len(policies)}")

    # Export to JSON
    output_file = f"{framework_id}_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'framework': {
                'id': framework_id,
                'name': framework_name,
                'full_name': framework.get('full_name', framework_name),
                'description': framework.get('description', ''),
                'url': framework.get('url', '')
            },
            'generated': datetime.now().isoformat(),
            'policies': [{'id': p['id'], 'name': p['name']} for p in policies],
            'compliance_data': compliance_data
        }, f, indent=2, default=str)

    print(f"\nDetailed report exported to: {output_file}")

def list_frameworks(frameworks):
    """List all available compliance frameworks"""
    print("\n" + "="*80)
    print("AVAILABLE COMPLIANCE FRAMEWORKS")
    print("="*80 + "\n")

    for framework_id, framework in sorted(frameworks.items()):
        if framework_id == 'custom-template':
            continue
        print(f"ID: {framework_id}")
        print(f"  Name: {framework['name']}")
        print(f"  Full Name: {framework.get('full_name', 'N/A')}")
        print(f"  Description: {framework.get('description', 'N/A')}")
        print(f"  Filter: {framework['policy_filter']['type']} = {framework['policy_filter']['value']}")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Universal Compliance Reporting for RHACS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate NIST 800-190 report
  python3 universal_compliance_report.py --framework nist-800-190

  # Generate PCI-DSS report
  python3 universal_compliance_report.py --framework pci-dss

  # Generate NIST 800-53 report
  python3 universal_compliance_report.py --framework nist-800-53

  # List all available frameworks
  python3 universal_compliance_report.py --list

  # Use custom framework configuration
  python3 universal_compliance_report.py --framework my-custom --config my_frameworks.yaml
        """
    )

    parser.add_argument(
        '--framework', '-f',
        help='Compliance framework ID (e.g., nist-800-190, pci-dss, nist-800-53)'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available compliance frameworks'
    )

    parser.add_argument(
        '--config', '-c',
        default='compliance_frameworks.yaml',
        help='Path to framework configuration file (default: compliance_frameworks.yaml)'
    )

    args = parser.parse_args()

    # Load framework configurations
    frameworks = load_frameworks(args.config)

    if args.list:
        list_frameworks(frameworks)
        return

    if not args.framework:
        print("ERROR: --framework is required (use --list to see available frameworks)")
        parser.print_help()
        sys.exit(1)

    # Generate report
    generate_compliance_report(args.framework, frameworks)

if __name__ == "__main__":
    main()
