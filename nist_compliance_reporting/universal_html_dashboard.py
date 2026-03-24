#!/usr/bin/env python3
"""
Universal HTML Dashboard Generator for RHACS Compliance

This script generates Red Hat branded HTML dashboards for any compliance framework.
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

def generate_html_dashboard(framework_id, frameworks):
    """Generate HTML dashboard for a specific framework"""

    if framework_id not in frameworks:
        print(f"ERROR: Unknown framework: {framework_id}")
        print(f"Available frameworks: {', '.join(frameworks.keys())}")
        sys.exit(1)

    framework = frameworks[framework_id]
    framework_name = framework['name']
    framework_full_name = framework.get('full_name', framework_name)

    print(f"\nGenerating HTML dashboard for {framework_name}...")
    print(f"Framework: {framework_full_name}")
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

    # Calculate statistics
    total_clusters = len(compliance_data)
    total_namespaces = sum(len(namespaces) for namespaces in compliance_data.values())
    total_deployments = sum(
        len(deployments_dict)
        for cluster in compliance_data.values()
        for deployments_dict in cluster.values()
    )

    # Count policy compliance
    policy_stats = defaultdict(lambda: {'total': 0, 'pass': 0, 'fail': 0})
    total_compliant = 0
    total_noncompliant = 0

    for cluster in compliance_data.values():
        for namespace in cluster.values():
            for deployment in namespace.values():
                deployment_passes = True
                for policy_name, result in deployment.items():
                    policy_stats[policy_name]['total'] += 1
                    if result['status'] == 'PASS':
                        policy_stats[policy_name]['pass'] += 1
                    else:
                        policy_stats[policy_name]['fail'] += 1
                        deployment_passes = False

                if deployment_passes:
                    total_compliant += 1
                else:
                    total_noncompliant += 1

    overall_pass_rate = (total_compliant / total_deployments * 100) if total_deployments > 0 else 0

    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_file = f"{framework_id}_compliance_dashboard_{timestamp}.html"

    print(f"\nGenerating HTML dashboard: {html_file}")

    # Generate HTML content with Red Hat branding
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{framework_name} Compliance Dashboard | Red Hat Advanced Cluster Security</title>
    <link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;500;700;900&family=Red+Hat+Text:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Red Hat Text', 'Helvetica Neue', Arial, sans-serif;
            background: #F5F5F5;
            color: #151515;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, #EE0000 0%, #A30000 100%);
            color: white;
            padding: 2.5rem 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .header h1 {{
            font-family: 'Red Hat Display', sans-serif;
            font-size: 2.5rem;
            font-weight: 900;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }}

        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.95;
            font-weight: 400;
        }}

        .header .framework-info {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.3);
            font-size: 0.95rem;
            opacity: 0.9;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #EE0000;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}

        .stat-card h3 {{
            font-family: 'Red Hat Display', sans-serif;
            color: #6A6E73;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}

        .stat-card .value {{
            font-family: 'Red Hat Display', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #151515;
            line-height: 1;
        }}

        .stat-card.success {{
            border-left-color: #3E8635;
        }}

        .stat-card.success .value {{
            color: #3E8635;
        }}

        .stat-card.danger {{
            border-left-color: #C9190B;
        }}

        .stat-card.danger .value {{
            color: #C9190B;
        }}

        .section {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .section h2 {{
            font-family: 'Red Hat Display', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            color: #151515;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #EE0000;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        th {{
            background: #F5F5F5;
            color: #151515;
            font-family: 'Red Hat Display', sans-serif;
            font-weight: 700;
            text-align: left;
            padding: 1rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #EE0000;
        }}

        td {{
            padding: 1rem;
            border-bottom: 1px solid #EDEDED;
        }}

        tr:hover {{
            background: #FAFAFA;
        }}

        .pass {{
            color: #3E8635;
            font-weight: 700;
        }}

        .fail {{
            color: #C9190B;
            font-weight: 700;
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .badge.pass {{
            background: #F0F8EF;
            color: #3E8635;
        }}

        .badge.fail {{
            background: #FDF1F0;
            color: #C9190B;
        }}

        .progress-bar {{
            width: 100%;
            height: 24px;
            background: #EDEDED;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3E8635 0%, #5BA352 100%);
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 0.85rem;
        }}

        .footer {{
            text-align: center;
            padding: 2rem;
            color: #6A6E73;
            font-size: 0.9rem;
        }}

        .footer a {{
            color: #EE0000;
            text-decoration: none;
            font-weight: 600;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}

        @media print {{
            .header {{
                background: #EE0000;
                color: white;
            }}
            .stat-card, .section {{
                box-shadow: none;
                border: 1px solid #EDEDED;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{framework_name} Compliance Dashboard</h1>
        <div class="subtitle">Red Hat Advanced Cluster Security</div>
        <div class="framework-info">
            <strong>{framework_full_name}</strong><br>
            Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Deployments</h3>
                <div class="value">{total_deployments}</div>
            </div>
            <div class="stat-card success">
                <h3>Compliant</h3>
                <div class="value">{total_compliant}</div>
            </div>
            <div class="stat-card danger">
                <h3>Non-Compliant</h3>
                <div class="value">{total_noncompliant}</div>
            </div>
            <div class="stat-card">
                <h3>Compliance Rate</h3>
                <div class="value">{overall_pass_rate:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Total Policies</h3>
                <div class="value">{len(policies)}</div>
            </div>
            <div class="stat-card">
                <h3>Clusters</h3>
                <div class="value">{total_clusters}</div>
            </div>
            <div class="stat-card">
                <h3>Namespaces</h3>
                <div class="value">{total_namespaces}</div>
            </div>
        </div>

        <div class="section">
            <h2>Policy Compliance Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Policy</th>
                        <th style="text-align: center;">Total</th>
                        <th style="text-align: center;">Passed</th>
                        <th style="text-align: center;">Failed</th>
                        <th>Pass Rate</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add policy rows
    for policy_name in sorted(policy_stats.keys()):
        stats = policy_stats[policy_name]
        total = stats['total']
        passed = stats['pass']
        failed = stats['fail']
        pass_rate = (passed / total * 100) if total > 0 else 0

        html_content += f"""
                    <tr>
                        <td style="font-weight: 500;">{policy_name}</td>
                        <td style="text-align: center;">{total}</td>
                        <td style="text-align: center;" class="pass">{passed}</td>
                        <td style="text-align: center;" class="fail">{failed}</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {pass_rate}%;">
                                    {pass_rate:.1f}%
                                </div>
                            </div>
                        </td>
                    </tr>
"""

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Deployment Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Cluster</th>
                        <th>Namespace</th>
                        <th>Deployment</th>
                        <th style="text-align: center;">Policies</th>
                        <th style="text-align: center;">Passed</th>
                        <th style="text-align: center;">Failed</th>
                        <th style="text-align: center;">Status</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add deployment rows
    for cluster in sorted(compliance_data.keys()):
        for namespace in sorted(compliance_data[cluster].keys()):
            for deployment in sorted(compliance_data[cluster][namespace].keys()):
                policy_results = compliance_data[cluster][namespace][deployment]
                total = len(policy_results)
                failed = sum(1 for r in policy_results.values() if r['status'] == 'FAIL')
                passed = total - failed
                status = 'PASS' if failed == 0 else 'FAIL'
                status_class = 'pass' if status == 'PASS' else 'fail'

                html_content += f"""
                    <tr>
                        <td>{cluster}</td>
                        <td>{namespace}</td>
                        <td style="font-weight: 500;">{deployment}</td>
                        <td style="text-align: center;">{total}</td>
                        <td style="text-align: center;" class="pass">{passed}</td>
                        <td style="text-align: center;" class="fail">{failed}</td>
                        <td style="text-align: center;">
                            <span class="badge {status_class}">{status}</span>
                        </td>
                    </tr>
"""

    html_content += f"""
                </tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        <p>Generated by <a href="https://www.redhat.com/en/technologies/cloud-computing/openshift/advanced-cluster-security-kubernetes" target="_blank">Red Hat Advanced Cluster Security</a></p>
        <p style="margin-top: 0.5rem; font-size: 0.85rem;">Framework: {framework_full_name}</p>
    </div>
</body>
</html>
"""

    # Write HTML file
    with open(html_file, 'w') as f:
        f.write(html_content)

    print(f"✓ HTML dashboard saved: {html_file}")

    # Summary
    print(f"\n{'='*80}")
    print(f"HTML DASHBOARD GENERATION COMPLETE - {framework_name}")
    print(f"{'='*80}")
    print(f"\nFramework:         {framework_name}")
    print(f"Total Clusters:    {total_clusters}")
    print(f"Total Namespaces:  {total_namespaces}")
    print(f"Total Deployments: {total_deployments}")
    print(f"Total Policies:    {len(policies)}")
    print(f"Compliance Rate:   {overall_pass_rate:.1f}%")
    print(f"\nGenerated File:    {html_file}")
    print(f"\nOpen in browser:   open {html_file}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description='Universal HTML Dashboard Generator for RHACS Compliance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate NIST 800-190 HTML dashboard
  python3 universal_html_dashboard.py --framework nist-800-190

  # Generate PCI-DSS HTML dashboard
  python3 universal_html_dashboard.py --framework pci-dss

  # Generate NIST 800-53 HTML dashboard
  python3 universal_html_dashboard.py --framework nist-800-53

  # Use custom framework configuration
  python3 universal_html_dashboard.py --framework my-custom --config my_frameworks.yaml
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

    # Generate HTML dashboard
    generate_html_dashboard(args.framework, frameworks)

if __name__ == "__main__":
    main()
