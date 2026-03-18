# NIST Compliance Report

Generate NIST 800-190 compliance reports from RHACS.

---

You are tasked with generating NIST 800-190 compliance reports from a Red Hat Advanced Cluster Security (RHACS) instance.

## Prerequisites Check

First, verify the following:

1. Check if we're in the correct directory:
   - Look for `nist_compliance_reporting/` directory
   - If not found, ask user for the project location

2. Verify environment variables are set:
   - `RHACS_URL` - The RHACS instance URL
   - `RHACS_API_TOKEN` - The API token for authentication
   - If not set, guide user to configure them

3. Check if Python dependencies are installed:
   - `requests`
   - `urllib3`
   - If missing, offer to install them

## Report Generation

Once prerequisites are met, generate compliance reports:

1. **Console Report with JSON Export**
   - Run: `python3 nist_compliance_reporting/nist_compliance_report.py`
   - This generates a detailed console output and JSON file

2. **CSV Reports**
   - Run: `python3 nist_compliance_reporting/generate_csv_report.py`
   - This generates 3 CSV files:
     * Detailed report (all deployments × policies)
     * Deployment summary
     * Policy summary

3. **HTML Dashboard**
   - Run: `python3 nist_compliance_reporting/generate_html_dashboard.py`
   - This generates an interactive HTML dashboard
   - Offer to open it in the browser

## Report Summary

After generation:
1. List the generated files with their sizes
2. Provide a brief summary of key findings:
   - Total deployments analyzed
   - Number of NIST policies checked
   - Top policy violations
   - Compliance percentage

3. Suggest next steps:
   - View HTML dashboard
   - Open CSV files for analysis
   - Review failed policies

## Error Handling

If errors occur:
- Missing environment variables → Show setup instructions
- API connection issues → Verify RHACS URL and token
- Missing scripts → Check if in correct directory or if files exist
- Python errors → Check dependencies

## Output Format

Present results in a clear, organized manner:
- Use formatted output for statistics
- Highlight critical issues
- Provide actionable recommendations
