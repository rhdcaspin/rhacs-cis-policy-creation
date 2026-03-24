# Universal Compliance Report Generator

Generate compliance reports for any framework supported by RHACS.

## Usage

This skill generates comprehensive compliance reports for any compliance framework including NIST 800-190, NIST 800-53, PCI-DSS, HIPAA, CIS, GDPR, SOC 2, ISO 27001, and FedRAMP.

## What it does

1. Validates environment variables (RHACS_URL, RHACS_API_TOKEN)
2. Lists available compliance frameworks
3. Prompts user to select a framework
4. Generates all report formats:
   - JSON compliance report
   - CSV reports (detailed, summary, policy summary)
   - HTML dashboard with Red Hat branding
5. Displays summary statistics

## Prompt

```
I'll generate a comprehensive compliance report for your chosen framework.

First, let me check the environment and list available frameworks.

cd /Users/dcaspin/Projects/claude/compliance_reporting/nist_compliance_reporting

# Check environment variables
if [ -z "$RHACS_URL" ] || [ -z "$RHACS_API_TOKEN" ]; then
    echo "ERROR: Missing required environment variables"
    echo "Please set:"
    echo "  export RHACS_URL='https://your-rhacs-instance.com'"
    echo "  export RHACS_API_TOKEN='your-api-token'"
    exit 1
fi

# List available frameworks
echo "Available Compliance Frameworks:"
echo "================================"
python3 universal_compliance_report.py --list

echo ""
echo "Which framework would you like to generate reports for?"
echo "Enter the framework ID (e.g., nist-800-190, pci-dss, nist-800-53, hipaa, cis-kubernetes):"
read FRAMEWORK_ID

echo ""
echo "Generating reports for: $FRAMEWORK_ID"
echo "======================================"
echo ""

# Generate JSON compliance report
echo "📊 Generating JSON compliance report..."
python3 universal_compliance_report.py --framework "$FRAMEWORK_ID"

# Generate CSV reports
echo ""
echo "📊 Generating CSV reports..."
python3 universal_csv_report.py --framework "$FRAMEWORK_ID"

# Generate HTML dashboard
echo ""
echo "📊 Generating HTML dashboard..."
python3 universal_html_dashboard.py --framework "$FRAMEWORK_ID"

echo ""
echo "✅ All reports generated successfully!"
echo ""
echo "Generated files:"
ls -lh ${FRAMEWORK_ID}_* 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "To view the HTML dashboard:"
echo "  open ${FRAMEWORK_ID}_compliance_dashboard_*.html"
```
