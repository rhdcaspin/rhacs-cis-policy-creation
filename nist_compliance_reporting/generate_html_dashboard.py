#!/usr/bin/env python3
"""
Generate HTML Dashboard from NIST 800-190 compliance data
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
        return []
    deployments = data['deployments']
    print(f"Found {len(deployments)} deployments")
    return deployments

def generate_html_dashboard():
    """Generate HTML dashboard for compliance data"""
    print("\n" + "="*80)
    print("RHACS NIST 800-190 Compliance Dashboard - HTML Generation")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    policies = get_nist_policies()
    if not policies:
        print("No NIST 800-190 policies found!")
        return

    deployments = get_all_deployments()

    # Track violations
    policies_with_violations = defaultdict(set)

    print("\nAnalyzing policy violations...")
    for policy in policies:
        policy_id = policy['id']
        policy_name = policy['name']
        print(f"  Checking policy: {policy_name}")

        violations = get_policy_violations(policy_id)

        for violation in violations:
            deployment_info = violation.get('deployment', {})
            deployment_id = deployment_info.get('id')
            if deployment_id:
                policies_with_violations[deployment_id].add(policy_id)

    # Calculate statistics
    total_deployments = len(deployments)
    total_policies = len(policies)

    # Policy statistics
    policy_stats = []
    for policy in policies:
        policy_id = policy['id']
        policy_name = policy['name']
        violation_count = sum(
            1 for deployment in deployments
            if policy_id in policies_with_violations.get(deployment.get('id'), set())
        )
        compliant_count = total_deployments - violation_count
        compliance_rate = (compliant_count / total_deployments * 100) if total_deployments > 0 else 0
        policy_stats.append({
            'name': policy_name,
            'violations': violation_count,
            'compliant': compliant_count,
            'rate': compliance_rate
        })

    # Deployment statistics
    fully_compliant = 0
    partially_compliant = 0
    non_compliant = 0

    deployment_stats = []
    for deployment in deployments:
        deployment_id = deployment.get('id')
        deployment_name = deployment.get('name')
        namespace = deployment.get('namespace')
        cluster = deployment.get('clusterName', 'Unknown')

        failed_count = len([p for p in policies if p['id'] in policies_with_violations.get(deployment_id, set())])
        passed_count = total_policies - failed_count
        pass_rate = (passed_count / total_policies * 100) if total_policies > 0 else 0

        if failed_count == 0:
            fully_compliant += 1
        elif passed_count > 0:
            partially_compliant += 1
        else:
            non_compliant += 1

        deployment_stats.append({
            'name': deployment_name,
            'namespace': namespace,
            'cluster': cluster,
            'passed': passed_count,
            'failed': failed_count,
            'rate': pass_rate
        })

    # Sort by compliance rate
    deployment_stats.sort(key=lambda x: x['rate'])
    policy_stats.sort(key=lambda x: x['rate'])

    # Generate HTML
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_file = f"nist_compliance_dashboard_{timestamp}.html"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NIST 800-190 Compliance Dashboard | Red Hat Advanced Cluster Security</title>
    <link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;500;700;900&family=Red+Hat+Text:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Red Hat Text', 'Overpass', 'Open Sans', Helvetica, Arial, sans-serif;
            background: #F5F5F5;
            color: #151515;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #EE0000 0%, #A30000 100%);
            color: white;
            padding: 35px 40px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            border-left: 5px solid #CC0000;
        }}
        .header h1 {{
            font-family: 'Red Hat Display', sans-serif;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        .header .subtitle {{
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 12px;
            opacity: 0.95;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 13px;
            font-weight: 400;
        }}
        .rhacs-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 28px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #EE0000;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .stat-card h3 {{
            font-family: 'Red Hat Display', sans-serif;
            font-size: 13px;
            color: #6A6E73;
            margin-bottom: 12px;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .stat-card .value {{
            font-family: 'Red Hat Display', sans-serif;
            font-size: 42px;
            font-weight: 900;
            margin-bottom: 8px;
            line-height: 1;
        }}
        .stat-card .subtext {{
            font-size: 13px;
            color: #8A8D90;
            font-weight: 500;
        }}
        .pass {{ color: #3E8635; }}
        .fail {{ color: #C9190B; }}
        .warn {{ color: #F0AB00; }}
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            border-top: 3px solid #EE0000;
        }}
        .section h2 {{
            font-family: 'Red Hat Display', sans-serif;
            margin-bottom: 25px;
            font-size: 26px;
            font-weight: 700;
            color: #151515;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 14px 12px;
            text-align: left;
            border-bottom: 1px solid #D2D2D2;
        }}
        th {{
            background: #F5F5F5;
            font-family: 'Red Hat Display', sans-serif;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            color: #6A6E73;
            letter-spacing: 0.5px;
        }}
        tr:hover {{ background: #FAFAFA; }}
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #EDEDED;
            border-radius: 2px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3E8635 0%, #5BA352 100%);
            transition: width 0.3s ease;
        }}
        .badge {{
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        .badge-pass {{
            background: #F3FAF2;
            color: #1E4F18;
            border: 1px solid #A2D99C;
        }}
        .badge-fail {{
            background: #FDF1F1;
            color: #7D1007;
            border: 1px solid #F4C8C5;
        }}
        .top-issues {{
            background: #FFF9E8;
            border-left: 5px solid #F0AB00;
            padding: 20px;
            margin-bottom: 25px;
        }}
        .top-issues h3 {{
            color: #795600;
            margin-bottom: 10px;
            font-family: 'Red Hat Display', sans-serif;
            font-weight: 700;
        }}
        .top-issues p {{
            color: #5C4A00;
            font-size: 14px;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #8A8D90;
            font-size: 13px;
            border-top: 2px solid #EDEDED;
            margin-top: 40px;
        }}
        .footer strong {{
            color: #EE0000;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Red Hat Advanced Cluster Security</h1>
            <div class="subtitle">NIST 800-190 Compliance Dashboard</div>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Instance: {RHACS_URL}</p>
            <span class="rhacs-badge">RHACS Compliance Report</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Deployments</h3>
                <div class="value">{total_deployments}</div>
                <div class="subtext">Across all clusters</div>
            </div>
            <div class="stat-card">
                <h3>Total Policies</h3>
                <div class="value">{total_policies}</div>
                <div class="subtext">NIST 800-190 policies</div>
            </div>
            <div class="stat-card">
                <h3>Fully Compliant</h3>
                <div class="value pass">{fully_compliant}</div>
                <div class="subtext">{(fully_compliant/total_deployments*100) if total_deployments > 0 else 0:.1f}% of deployments</div>
            </div>
            <div class="stat-card">
                <h3>Non-Compliant</h3>
                <div class="value fail">{total_deployments - fully_compliant}</div>
                <div class="subtext">{((total_deployments - fully_compliant)/total_deployments*100) if total_deployments > 0 else 0:.1f}% need attention</div>
            </div>
        </div>

        <div class="top-issues">
            <h3>⚠ Top Policy Issues</h3>
            <p>The following policies have the most violations across deployments:</p>
        </div>

        <div class="section">
            <h2>Policy Compliance Overview</h2>
            <table>
                <thead>
                    <tr>
                        <th>Policy</th>
                        <th>Compliant</th>
                        <th>Violations</th>
                        <th>Compliance Rate</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
"""

    for policy in policy_stats:
        html_content += f"""
                    <tr>
                        <td>{policy['name']}</td>
                        <td>{policy['compliant']}</td>
                        <td class="fail">{policy['violations']}</td>
                        <td>{policy['rate']:.1f}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {policy['rate']}%"></div>
                            </div>
                        </td>
                    </tr>
"""

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Deployment Compliance (Top 50 Least Compliant)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Deployment</th>
                        <th>Namespace</th>
                        <th>Cluster</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Pass Rate</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""

    for deployment in deployment_stats[:50]:
        status_badge = 'badge-pass' if deployment['failed'] == 0 else 'badge-fail'
        status_text = 'PASS' if deployment['failed'] == 0 else 'FAIL'

        html_content += f"""
                    <tr>
                        <td><strong>{deployment['name']}</strong></td>
                        <td>{deployment['namespace']}</td>
                        <td>{deployment['cluster']}</td>
                        <td class="pass">{deployment['passed']}</td>
                        <td class="fail">{deployment['failed']}</td>
                        <td>{deployment['rate']:.1f}%</td>
                        <td><span class="badge {status_badge}">{status_text}</span></td>
                    </tr>
"""

    html_content += f"""
                </tbody>
            </table>
            <p style="margin-top: 15px; color: #8A8D90; font-size: 12px;">
                Showing top 50 least compliant deployments out of {total_deployments} total
            </p>
        </div>

        <div class="section">
            <h2>Overall Compliance Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Average Compliance Rate</h3>
                    <div class="value">{sum(d['rate'] for d in deployment_stats) / len(deployment_stats) if deployment_stats else 0:.1f}%</div>
                </div>
                <div class="stat-card">
                    <h3>Best Performing Policy</h3>
                    <div class="value" style="font-size: 16px;">{policy_stats[-1]['name'] if policy_stats else 'N/A'}</div>
                    <div class="subtext pass">{policy_stats[-1]['rate'] if policy_stats else 0:.1f}% compliant</div>
                </div>
                <div class="stat-card">
                    <h3>Needs Most Attention</h3>
                    <div class="value" style="font-size: 16px;">{policy_stats[0]['name'] if policy_stats else 'N/A'}</div>
                    <div class="subtext fail">{policy_stats[0]['violations'] if policy_stats else 0} violations</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Powered by <strong>Red Hat Advanced Cluster Security</strong></p>
            <p style="margin-top: 8px; font-size: 12px;">
                NIST 800-190 Application Container Security Guide Compliance
            </p>
        </div>
    </div>
</body>
</html>
"""

    with open(html_file, 'w') as f:
        f.write(html_content)

    print(f"\n✅ HTML Dashboard generated: {html_file}")
    print(f"\nOpen this file in your web browser to view the interactive dashboard.")

if __name__ == "__main__":
    generate_html_dashboard()
