# Quick Compliance Setup

One-command setup: Create policies and generate reports for a compliance framework.

## Usage

This skill provides a complete workflow to set up compliance reporting for a framework. It creates the policies in RHACS, then generates all report formats.

## What it does

1. Validates environment variables
2. Prompts for framework selection
3. Creates policies in RHACS (if available)
4. Generates JSON compliance report
5. Generates CSV reports
6. Generates HTML dashboard
7. Opens the dashboard in browser

## Prompt

```
I'll set up complete compliance reporting for your chosen framework.

cd /Users/dcaspin/Projects/claude/compliance_reporting/nist_compliance_reporting

# Check environment variables
if [ -z "$RHACS_URL" ] || [ -z "$RHACS_API_TOKEN" ]; then
    echo "❌ ERROR: Missing required environment variables"
    echo ""
    echo "Please set:"
    echo "  export RHACS_URL='https://your-rhacs-instance.com'"
    echo "  export RHACS_API_TOKEN='your-api-token'"
    echo ""
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Quick Compliance Setup - RHACS                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# List available frameworks
echo "Available Frameworks:"
echo "===================="
python3 universal_compliance_report.py --list | grep "^ID:" | sed 's/ID: /  • /'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Select a framework (e.g., pci-dss, nist-800-190, hipaa):"
read FRAMEWORK_ID

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Policy Creation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if policy creation script exists for this framework
case "$FRAMEWORK_ID" in
    pci-dss|pci)
        echo "Creating PCI-DSS 4.0 policies in RHACS..."
        echo ""
        python3 create_pci_dss_policies.py
        FRAMEWORK_ID="pci-dss"  # Normalize
        ;;
    nist-800-190|nist-190)
        echo "ℹ️  NIST 800-190 policies should already exist in RHACS."
        echo "If not, please create them manually in the RHACS console."
        FRAMEWORK_ID="nist-800-190"  # Normalize
        ;;
    *)
        echo "ℹ️  No automated policy creation available for $FRAMEWORK_ID"
        echo "Please ensure policies exist in RHACS with category matching this framework."
        echo ""
        echo "Continue with report generation? (y/n)"
        read CONTINUE
        if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
            exit 0
        fi
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Report Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Generate JSON compliance report
echo "📊 Generating JSON compliance report..."
python3 universal_compliance_report.py --framework "$FRAMEWORK_ID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Generate CSV reports
echo "📊 Generating CSV reports..."
python3 universal_csv_report.py --framework "$FRAMEWORK_ID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Generate HTML dashboard
echo "📊 Generating HTML dashboard..."
python3 universal_html_dashboard.py --framework "$FRAMEWORK_ID"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   ✅ Compliance Setup Complete!                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# List generated files
echo "Generated Files:"
ls -lh ${FRAMEWORK_ID}_* 2>/dev/null | awk '{print "  📄 " $9 " (" $5 ")"}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. View HTML Dashboard:"
DASHBOARD=$(ls -t ${FRAMEWORK_ID}_compliance_dashboard_*.html 2>/dev/null | head -1)
if [ -n "$DASHBOARD" ]; then
    echo "   open $DASHBOARD"
    echo ""
    echo "   Opening in browser..."
    open "$DASHBOARD" 2>/dev/null || echo "   (Please open manually)"
fi

echo ""
echo "2. Review policies in RHACS:"
echo "   ${RHACS_URL}/main/policies"
echo ""
echo "3. Share reports with your team"
echo ""
```
