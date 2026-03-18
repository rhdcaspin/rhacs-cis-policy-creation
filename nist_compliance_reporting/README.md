# RHACS NIST 800-190 Compliance Reporting Tool

This tool generates compliance reports for NIST 800-190 policies from Red Hat Advanced Cluster Security (RHACS).

## Overview

The compliance reporting tool connects to your RHACS instance, fetches all NIST 800-190 policies and their violations, and generates comprehensive reports showing Pass/Fail status for each deployment across all clusters and namespaces.

## Features

- **Policy-based Compliance**: Automatically fetches all NIST 800-190 policies from RHACS
- **Violation Detection**: Identifies deployments with policy violations
- **Multi-level Reporting**: Reports organized by Cluster → Namespace → Deployment
- **Multiple Output Formats**:
  - Console output with detailed breakdown
  - JSON for programmatic access
  - CSV files for spreadsheet analysis

## NIST 800-190 Policies Covered

The tool currently monitors 12 NIST 800-190 policies:

1. **4.1.1** - Image Vulnerabilities Not Scanned
2. **4.1.2** - Insecure Container Images
3. **4.1.4** - Root User in Container
4. **4.4.1** - Privileged Containers
5. **4.4.2** - Host Namespace Sharing
6. **4.4.4** - Dangerous Linux Capabilities
7. **4.4.5** - Privilege Escalation Allowed
8. **4.5.1** - Sensitive Host Paths Mounted
9. **4.5.2** - HostPath Volumes Used
10. **Runtime-1** - Unauthorized Process Execution
11. **Runtime-2** - Cryptocurrency Mining Detection
12. **Runtime-3** - Package Manager Usage

## Requirements

- Python 3.6+
- Required packages: `requests`, `urllib3`

Install dependencies:
```bash
pip install requests urllib3
```

## Configuration

### Security Best Practices

**IMPORTANT**: This tool uses environment variables for configuration to avoid hardcoding sensitive credentials.

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your RHACS credentials:
```bash
RHACS_URL=https://your-rhacs-instance.com
RHACS_API_TOKEN=your-api-token-here
RHACS_VERIFY_SSL=false  # Set to 'true' for production
```

3. Load environment variables before running scripts:
```bash
# Option 1: Export manually
export RHACS_URL='https://your-rhacs-instance.com'
export RHACS_API_TOKEN='your-api-token-here'

# Option 2: Use source (if using .env file)
set -a
source .env
set +a
```

**Note**: The `.env` file is automatically excluded from git via `.gitignore` to prevent credential exposure.

### Generate API Token

To generate an API token in RHACS:
1. Navigate to **Platform Configuration** > **Integrations**
2. Click **API Token** and create a new token
3. Ensure the token has **Admin** or **Analyst** role for read access

## Usage

### 1. Generate Console Report with JSON Export

```bash
python3 nist_compliance_report.py
```

This will:
- Print a detailed console report showing all clusters, namespaces, and deployments
- Highlight which policies failed for each deployment
- Export detailed JSON data to `nist_compliance_report_YYYYMMDD_HHMMSS.json`

### 2. Generate CSV Reports

```bash
python3 generate_csv_report.py
```

This generates three CSV files:

#### a) Detailed Report (`nist_compliance_detailed_YYYYMMDD_HHMMSS.csv`)
Contains one row per deployment per policy with columns:
- Cluster
- Namespace
- Deployment
- Policy
- Status (PASS/FAIL)

#### b) Deployment Summary (`nist_compliance_summary_YYYYMMDD_HHMMSS.csv`)
Contains one row per deployment with aggregated statistics:
- Cluster
- Namespace
- Deployment
- Total Policies
- Passed
- Failed
- Pass Rate %
- Status (PASS/FAIL)

#### c) Policy Summary (`nist_policy_summary_YYYYMMDD_HHMMSS.csv`)
Contains one row per policy with compliance statistics:
- Policy Name
- Total Deployments
- Violations
- Compliance Rate %

## Output Examples

### Console Output
```
################################################################################
CLUSTER: production-cluster
################################################################################

  Namespace: web-services
  ----------------------------------------------------------------------------

    Deployment: frontend-app
      Summary: 10/12 policies PASS, 2/12 policies FAIL

      Failed Policies:
        ❌ NIST-800-190-4.1.4 - Root User in Container
        ❌ NIST-800-190-4.4.5 - Privilege Escalation Allowed
```

### CSV Summary Example
```csv
Cluster,Namespace,Deployment,Total Policies,Passed,Failed,Pass Rate %,Status
production,web-services,frontend-app,12,10,2,83.3,FAIL
production,web-services,backend-api,12,12,0,100.0,PASS
```

## Compliance Logic

- **PASS**: A deployment passes a policy if there are NO violations for that policy
- **FAIL**: A deployment fails a policy if there is at least ONE violation for that policy
- **Deployment Status**:
  - PASS: All policies pass (0 failures)
  - FAIL: At least one policy fails

## Files Generated

Each run generates timestamped files:

- `nist_compliance_report_YYYYMMDD_HHMMSS.json` - Full JSON export
- `nist_compliance_detailed_YYYYMMDD_HHMMSS.csv` - Detailed CSV
- `nist_compliance_summary_YYYYMMDD_HHMMSS.csv` - Deployment summary CSV
- `nist_policy_summary_YYYYMMDD_HHMMSS.csv` - Policy summary CSV

## API Endpoints Used

The tool uses the following RHACS API endpoints:

- `GET /v1/policies` - Fetch all policies
- `GET /v1/alerts` - Fetch policy violations (alerts)
- `GET /v1/deployments` - Fetch all deployments

## Troubleshooting

### SSL Certificate Warnings
The tool disables SSL verification for the demo environment. For production use, remove the `verify=False` parameter and ensure proper SSL certificates.

### API Token Expiration
If you receive authentication errors, your API token may have expired. Generate a new token from RHACS and update the scripts.

### No Data Returned
Ensure:
1. Your API token has the correct permissions (Admin role)
2. The RHACS URL is accessible from your network
3. There are policies and deployments in your RHACS instance

## Security Considerations

- Store API tokens securely (use environment variables in production)
- Do not commit API tokens to version control
- Use proper SSL verification in production environments
- Implement token rotation for long-running deployments

## Example Use Cases

1. **Compliance Auditing**: Generate regular reports for compliance review
2. **Trend Analysis**: Compare reports over time to track compliance improvements
3. **Policy Effectiveness**: Use policy summary to identify which policies have the most violations
4. **Deployment Prioritization**: Identify which deployments need immediate attention
5. **Namespace/Cluster Analysis**: Identify which areas of infrastructure need security improvements

## License

This tool is provided as-is for compliance reporting purposes.
