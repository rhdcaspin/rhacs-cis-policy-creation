# NIST 800-190 Compliance Reporting - Quick Start

## ⚙️ Initial Setup (First Time Only)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your RHACS credentials
nano .env  # or use your preferred editor

# 3. Set environment variables
export RHACS_URL='https://your-rhacs-instance.com'
export RHACS_API_TOKEN='your-api-token-here'
```

## 🚀 Quick Commands

```bash
# Generate all reports at once
python3 nist_compliance_report.py && \
python3 generate_csv_report.py && \
python3 generate_html_dashboard.py

# View the HTML dashboard
open nist_compliance_dashboard_*.html
```

## 📊 Individual Reports

```bash
# Console report with JSON export
python3 nist_compliance_report.py

# CSV reports (detailed, summary, policy overview)
python3 generate_csv_report.py

# Interactive HTML dashboard
python3 generate_html_dashboard.py
```

## 📁 Output Files

| File Type | Description | Size | Use Case |
|-----------|-------------|------|----------|
| `*.json` | Full data export | ~800 KB | API integration, automation |
| `*_detailed.csv` | All deployments × policies | ~680 KB | Deep analysis, filtering |
| `*_summary.csv` | Deployment summaries | ~40 KB | Quick review, trending |
| `*_policy_summary.csv` | Policy statistics | <1 KB | Policy effectiveness |
| `*.html` | Interactive dashboard | N/A | Executive reporting |

## 🎯 Common Use Cases

### Find All Failing Deployments
```bash
# Open summary CSV and filter for Status = FAIL
open nist_compliance_summary_*.csv
```

### Check Specific Policy Compliance
```bash
# Open detailed CSV and filter by Policy column
open nist_compliance_detailed_*.csv
```

### Executive Summary
```bash
# Open HTML dashboard in browser
open nist_compliance_dashboard_*.html
```

### View Specific Namespace
```bash
# Filter detailed CSV by Namespace column
```

## 📈 Report Structure

```
Cluster
  ├── Namespace 1
  │   ├── Deployment A
  │   │   ├── Policy 1: PASS/FAIL
  │   │   ├── Policy 2: PASS/FAIL
  │   │   └── ...
  │   └── Deployment B
  │       └── ...
  └── Namespace 2
      └── ...
```

## 🔍 Understanding Results

- **PASS**: No violations for this policy on this deployment
- **FAIL**: At least 1 violation exists
- **Deployment Status**: FAIL if ANY policy fails

## ⚠️ Top Issues to Address

Based on current data:

1. **Root User in Container** (233 violations) - Highest priority
2. **Privilege Escalation Allowed** (217 violations) - High priority
3. **HostPath Volumes Used** (87 violations) - Medium priority

## 🔄 Scheduling Regular Reports

### Using Cron (macOS/Linux)
```bash
# Edit crontab
crontab -e

# Add daily report at 9 AM
0 9 * * * cd /path/to/compliance_reporting && python3 generate_html_dashboard.py
```

### Manual Schedule
Run these commands weekly to track compliance trends:
```bash
cd /Users/dcaspin/Projects/claude/compliance_reporting
python3 generate_csv_report.py
python3 generate_html_dashboard.py
```

## 🔧 Customization

### Change RHACS Instance
Edit in each Python script:
```python
RHACS_URL = "https://your-rhacs-instance.com"
API_TOKEN = "your-api-token"
```

### Filter Specific Clusters
Modify the scripts to add cluster filtering in the `get_all_deployments()` function.

## 📞 Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review the generated reports for data accuracy
3. Verify API token has correct permissions

## 🎓 Learn More

- **NIST 800-190**: Application Container Security Guide
- **RHACS Documentation**: https://docs.openshift.com/acs/
- **Report Format**: See README.md for detailed explanation
