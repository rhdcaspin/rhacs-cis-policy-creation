#!/usr/bin/env python3
"""
Generate CSV summary from NIST 800-190 compliance data
"""

import requests
import json
import csv
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

def generate_csv_reports():
    """Generate CSV reports for compliance data"""
    print("\n" + "="*80)
    print("RHACS NIST 800-190 Compliance Report - CSV Generation")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    policies = get_nist_policies()
    if not policies:
        print("No NIST 800-190 policies found!")
        return

    deployments = get_all_deployments()

    # Track violations
    policies_with_violations = defaultdict(set)
    violation_details = defaultdict(lambda: defaultdict(list))

    print("\nAnalyzing policy violations...")
    for policy in policies:
        policy_id = policy['id']
        policy_name = policy['name']
        print(f"  Checking policy: {policy_name}")

        violations = get_policy_violations(policy_id)

        for violation in violations:
            deployment_info = violation.get('deployment', {})
            deployment_id = deployment_info.get('id')
            deployment_name = deployment_info.get('name')
            namespace = deployment_info.get('namespace')
            cluster_name = deployment_info.get('clusterName', 'Unknown')

            if deployment_id:
                policies_with_violations[deployment_id].add(policy_id)
                violation_details[deployment_id][policy_id].append({
                    'deployment_name': deployment_name,
                    'namespace': namespace,
                    'cluster': cluster_name,
                    'policy_name': policy_name,
                    'violation_time': violation.get('time', 'Unknown')
                })

    # Generate detailed CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    detailed_csv = f"nist_compliance_detailed_{timestamp}.csv"

    print(f"\nGenerating detailed CSV: {detailed_csv}")
    with open(detailed_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Cluster', 'Namespace', 'Deployment', 'Policy', 'Status'
        ])

        for deployment in deployments:
            deployment_id = deployment.get('id')
            deployment_name = deployment.get('name')
            namespace = deployment.get('namespace')
            cluster_name = deployment.get('clusterName', 'Unknown')

            for policy in policies:
                policy_id = policy['id']
                policy_name = policy['name']
                has_violation = policy_id in policies_with_violations.get(deployment_id, set())
                status = 'FAIL' if has_violation else 'PASS'

                writer.writerow([
                    cluster_name,
                    namespace,
                    deployment_name,
                    policy_name,
                    status
                ])

    # Generate summary CSV by deployment
    summary_csv = f"nist_compliance_summary_{timestamp}.csv"

    print(f"Generating summary CSV: {summary_csv}")
    with open(summary_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Cluster', 'Namespace', 'Deployment',
            'Total Policies', 'Passed', 'Failed', 'Pass Rate %', 'Status'
        ])

        for deployment in deployments:
            deployment_id = deployment.get('id')
            deployment_name = deployment.get('name')
            namespace = deployment.get('namespace')
            cluster_name = deployment.get('clusterName', 'Unknown')

            total_policies = len(policies)
            failed_count = len([p for p in policies if p['id'] in policies_with_violations.get(deployment_id, set())])
            passed_count = total_policies - failed_count
            pass_rate = (passed_count / total_policies * 100) if total_policies > 0 else 0
            overall_status = 'PASS' if failed_count == 0 else 'FAIL'

            writer.writerow([
                cluster_name,
                namespace,
                deployment_name,
                total_policies,
                passed_count,
                failed_count,
                f"{pass_rate:.1f}",
                overall_status
            ])

    # Generate policy summary CSV
    policy_summary_csv = f"nist_policy_summary_{timestamp}.csv"

    print(f"Generating policy summary CSV: {policy_summary_csv}")
    with open(policy_summary_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Policy Name', 'Total Deployments', 'Violations', 'Compliance Rate %'
        ])

        total_deployments = len(deployments)
        for policy in policies:
            policy_id = policy['id']
            policy_name = policy['name']

            # Count how many deployments have violations for this policy
            violation_count = sum(
                1 for deployment in deployments
                if policy_id in policies_with_violations.get(deployment.get('id'), set())
            )

            compliant_count = total_deployments - violation_count
            compliance_rate = (compliant_count / total_deployments * 100) if total_deployments > 0 else 0

            writer.writerow([
                policy_name,
                total_deployments,
                violation_count,
                f"{compliance_rate:.1f}"
            ])

    print("\n" + "="*80)
    print("CSV REPORTS GENERATED")
    print("="*80)
    print(f"\n1. Detailed Report:     {detailed_csv}")
    print(f"2. Deployment Summary:  {summary_csv}")
    print(f"3. Policy Summary:      {policy_summary_csv}")
    print("\nThese CSV files can be opened in Excel, Google Sheets, or any spreadsheet application.")

if __name__ == "__main__":
    generate_csv_reports()
