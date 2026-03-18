#!/usr/bin/env python3
"""
RHACS NIST 800-190 Compliance Reporting Tool

This script generates compliance reports for NIST 800-190 policies from RHACS.
It fetches all policies with NIST 800-190 in their name, retrieves violations,
and generates a report showing Pass/Fail status for each deployment in each namespace and cluster.
"""

import requests
import json
import os
import sys
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

def get_nist_policies():
    """Fetch all NIST 800-190 policies"""
    print("Fetching NIST 800-190 policies...")
    data = api_request("/v1/policies", params={"query": "Category:NIST"})

    if not data or 'policies' not in data:
        print("No policies found")
        return []

    # Filter for NIST-800-190 policies
    nist_policies = [p for p in data['policies'] if 'NIST-800-190' in p.get('name', '')]
    print(f"Found {len(nist_policies)} NIST 800-190 policies")
    return nist_policies

def get_policy_violations(policy_id):
    """Fetch violations for a specific policy"""
    data = api_request(f"/v1/alerts", params={"query": f"Policy Id:{policy_id}"})

    if not data or 'alerts' not in data:
        return []

    return data['alerts']

def get_all_deployments():
    """Fetch all deployments from RHACS"""
    print("Fetching deployments...")
    data = api_request("/v1/deployments")

    if not data or 'deployments' not in data:
        print("No deployments found")
        return []

    deployments = data['deployments']
    print(f"Found {len(deployments)} deployments")
    return deployments

def generate_compliance_report():
    """Generate NIST 800-190 compliance report"""
    print("\n" + "="*80)
    print("RHACS NIST 800-190 Compliance Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Get all NIST policies
    policies = get_nist_policies()

    if not policies:
        print("No NIST 800-190 policies found!")
        return

    # Get all deployments
    deployments = get_all_deployments()

    # Create structure: cluster -> namespace -> deployment -> policy results
    compliance_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    # Track which policies have violations
    policies_with_violations = defaultdict(set)

    print("\nAnalyzing policy violations...")
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
    print("COMPLIANCE REPORT BY CLUSTER/NAMESPACE/DEPLOYMENT")
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

    print(f"Total Clusters:    {total_clusters}")
    print(f"Total Namespaces:  {total_namespaces}")
    print(f"Total Deployments: {total_deployments}")
    print(f"Total Policies:    {len(policies)}")

    # Export to JSON
    output_file = f"nist_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'policies': [{'id': p['id'], 'name': p['name']} for p in policies],
            'compliance_data': compliance_data
        }, f, indent=2, default=str)

    print(f"\nDetailed report exported to: {output_file}")

if __name__ == "__main__":
    generate_compliance_report()
