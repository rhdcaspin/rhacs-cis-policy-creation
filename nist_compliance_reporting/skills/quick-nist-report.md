# Quick NIST Report

Generate all NIST 800-190 compliance reports at once.

---

You are generating a quick NIST 800-190 compliance report from RHACS.

## Quick Execution

1. Navigate to the project directory if not already there
2. Verify environment variables `RHACS_URL` and `RHACS_API_TOKEN` are set
3. Run all three report generators in sequence:
   ```bash
   cd nist_compliance_reporting
   python3 nist_compliance_report.py && \
   python3 generate_csv_report.py && \
   python3 generate_html_dashboard.py
   ```

4. Open the HTML dashboard automatically:
   ```bash
   open nist_compliance_dashboard_*.html
   ```

5. Provide a one-line summary of the results:
   - Total deployments
   - Compliance rate
   - Top issue

Keep it fast and concise. If errors occur, suggest running `/nist-compliance-report` for the full guided experience.
