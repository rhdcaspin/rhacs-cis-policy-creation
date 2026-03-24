#!/usr/bin/env python3
"""
Universal CSV Report Generator for RHACS Compliance

This script generates CSV reports for any compliance framework supported by RHACS.
Supports NIST 800-190, NIST 800-53, PCI-DSS, HIPAA, CIS, GDPR, SOC 2, ISO 27001, FedRAMP, and custom frameworks.
"""

import requests
import json
import os
import sys
import csv
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
        data = api_request("/v1/policies", params={"query": f"Category:{filter_value}"})
    elif filter_type == 'name_prefix':
        data = api_request("/v1/policies", params={"query": f"Policy:{filter_value}"})
    elif filter_type == 'name_contains':
        data = api_request("/v1/policies")
    elif filter_type == 'tag':
        data = api_request("/v1/policies", params={"query": f"Tag:{filter_value}"})
    else:
        print(f"ERROR: Unknown filter type: {filter_type}")
        return []

    if not data or 'policies' not in data:
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
        return []
    return data['deployments']

def generate_csv_reports(framework_id, frameworks):
    """Generate CSV reports for a specific framework"""

    if framework_id not in frameworks:
        print(f"ERROR: Unknown framework: {framework_id}")
        print(f"Available frameworks: {', '.join(frameworks.keys())}")
        sys.exit(1)

    framework = frameworks[framework_id]
    framework_name = framework['name']

    print(f"\nGenerating CSV reports for {framework_name}...")
    print(f"Framework: {framework.get('full_name', framework_name)}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Get policies for this framework
    print(f"Fetching {framework_name} policies...")
    policies = get_policies_for_framework(framework)

    if not policies:
        print(f"No policies found for {framework_name}!")
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

        violations = get_policy_violations(policy_id)

        # Track deployments with violations for this policy
        for violation in violations:
            deployment_info = violation.get('deployment', {})
            deployment_id = deployment_info.get('id')

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

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Generate 1: Detailed Report
    detailed_file = f"{framework_id}_compliance_detailed_{timestamp}.csv"
    print(f"\nGenerating detailed report: {detailed_file}")

    with open(detailed_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Cluster', 'Namespace', 'Deployment', 'Policy', 'Status', 'Framework'])

        for cluster in sorted(compliance_data.keys()):
            for namespace in sorted(compliance_data[cluster].keys()):
                for deployment in sorted(compliance_data[cluster][namespace].keys()):
                    for policy_name, result in sorted(compliance_data[cluster][namespace][deployment].items()):
                        writer.writerow([
                            cluster,
                            namespace,
                            deployment,
                            policy_name,
                            result['status'],
                            framework_name
                        ])

    print(f"✓ Detailed report saved: {detailed_file}")

    # Generate 2: Summary Report by Deployment
    summary_file = f"{framework_id}_compliance_summary_{timestamp}.csv"
    print(f"Generating summary report: {summary_file}")

    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Cluster', 'Namespace', 'Deployment', 'Total Policies', 'Passed', 'Failed', 'Pass Rate', 'Framework'])

        for cluster in sorted(compliance_data.keys()):
            for namespace in sorted(compliance_data[cluster].keys()):
                for deployment in sorted(compliance_data[cluster][namespace].keys()):
                    policy_results = compliance_data[cluster][namespace][deployment]

                    total = len(policy_results)
                    failed = sum(1 for r in policy_results.values() if r['status'] == 'FAIL')
                    passed = total - failed
                    pass_rate = f"{(passed/total*100):.1f}%" if total > 0 else "N/A"

                    writer.writerow([
                        cluster,
                        namespace,
                        deployment,
                        total,
                        passed,
                        failed,
                        pass_rate,
                        framework_name
                    ])

    print(f"✓ Summary report saved: {summary_file}")

    # Generate 3: Policy Summary Report
    policy_summary_file = f"{framework_id}_policy_summary_{timestamp}.csv"
    print(f"Generating policy summary: {policy_summary_file}")

    # Count deployments per policy
    policy_stats = defaultdict(lambda: {'total': 0, 'pass': 0, 'fail': 0})

    for cluster in compliance_data.values():
        for namespace in cluster.values():
            for deployment in namespace.values():
                for policy_name, result in deployment.items():
                    policy_stats[policy_name]['total'] += 1
                    if result['status'] == 'PASS':
                        policy_stats[policy_name]['pass'] += 1
                    else:
                        policy_stats[policy_name]['fail'] += 1

    with open(policy_summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Policy', 'Total Deployments', 'Passed', 'Failed', 'Pass Rate', 'Framework'])

        for policy_name in sorted(policy_stats.keys()):
            stats = policy_stats[policy_name]
            total = stats['total']
            passed = stats['pass']
            failed = stats['fail']
            pass_rate = f"{(passed/total*100):.1f}%" if total > 0 else "N/A"

            writer.writerow([
                policy_name,
                total,
                passed,
                failed,
                pass_rate,
                framework_name
            ])

    print(f"✓ Policy summary saved: {policy_summary_file}")

    # Summary statistics
    total_clusters = len(compliance_data)
    total_namespaces = sum(len(namespaces) for namespaces in compliance_data.values())
    total_deployments = sum(
        len(deployments)
        for cluster in compliance_data.values()
        for deployments in cluster.values()
    )

    print(f"\n{'='*80}")
    print(f"CSV REPORT GENERATION COMPLETE - {framework_name}")
    print(f"{'='*80}")
    print(f"\nFramework:         {framework_name}")
    print(f"Total Clusters:    {total_clusters}")
    print(f"Total Namespaces:  {total_namespaces}")
    print(f"Total Deployments: {total_deployments}")
    print(f"Total Policies:    {len(policies)}")
    print(f"\nGenerated Files:")
    print(f"  1. {detailed_file}")
    print(f"  2. {summary_file}")
    print(f"  3. {policy_summary_file}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description='Universal CSV Report Generator for RHACS Compliance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate NIST 800-190 CSV reports
  python3 universal_csv_report.py --framework nist-800-190

  # Generate PCI-DSS CSV reports
  python3 universal_csv_report.py --framework pci-dss

  # Generate NIST 800-53 CSV reports
  python3 universal_csv_report.py --framework nist-800-53

  # Use custom framework configuration
  python3 universal_csv_report.py --framework my-custom --config my_frameworks.yaml
        """
    )

    parser.add_argument(
        '--framework', '-f',
        required=True,
        help='Compliance framework ID (e.g., nist-800-190, pci-dss, nist-800-53)'
    )

    parser.add_argument(
        '--config', '-c',
        default='compliance_frameworks.yaml',
        help='Path to framework configuration file (default: compliance_frameworks.yaml)'
    )

    args = parser.parse_args()

    # Load framework configurations
    frameworks = load_frameworks(args.config)

    # Generate CSV reports
    generate_csv_reports(args.framework, frameworks)

if __name__ == "__main__":
    main()
