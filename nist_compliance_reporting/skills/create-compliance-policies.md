# Create Compliance Policies

Create compliance policies in RHACS for various frameworks.

## Usage

This skill creates compliance policies in RHACS for different compliance frameworks. Currently supports PCI-DSS 4.0 with more frameworks coming soon.

## What it does

1. Validates environment variables (RHACS_URL, RHACS_API_TOKEN)
2. Shows available policy creation scripts
3. Prompts user to select a framework
4. Creates policies in RHACS
5. Displays creation summary
6. Provides next steps for generating reports

## Prompt

```
I'll create compliance policies in RHACS for your chosen framework.

cd /Users/dcaspin/Projects/claude/compliance_reporting/nist_compliance_reporting

# Check environment variables
if [ -z "$RHACS_URL" ] || [ -z "$RHACS_API_TOKEN" ]; then
    echo "ERROR: Missing required environment variables"
    echo "Please set:"
    echo "  export RHACS_URL='https://your-rhacs-instance.com'"
    echo "  export RHACS_API_TOKEN='your-api-token'"
    exit 1
fi

echo "Available Policy Creation Scripts:"
echo "=================================="
echo ""
echo "1. PCI-DSS 4.0 (Payment Card Industry Data Security Standard)"
echo "   - 15 comprehensive policies covering all 12 PCI-DSS requirements"
echo "   - Network security, access control, encryption, vulnerability management"
echo ""
echo "More frameworks coming soon:"
echo "  - HIPAA (Health Insurance Portability and Accountability Act)"
echo "  - NIST 800-53 (Security and Privacy Controls)"
echo "  - ISO 27001 (Information Security Management)"
echo ""
echo "Which framework would you like to create policies for?"
echo "Enter: pci-dss"
read FRAMEWORK

case "$FRAMEWORK" in
    pci-dss|pci|PCI-DSS|PCI)
        echo ""
        echo "Creating PCI-DSS 4.0 Policies in RHACS"
        echo "======================================"
        echo ""
        python3 create_pci_dss_policies.py

        echo ""
        echo "Next Steps:"
        echo "==========="
        echo ""
        echo "1. Review policies in RHACS console:"
        echo "   ${RHACS_URL}/main/policies"
        echo ""
        echo "2. Generate compliance reports:"
        echo "   python3 universal_compliance_report.py --framework pci-dss"
        echo "   python3 universal_html_dashboard.py --framework pci-dss"
        echo ""
        echo "3. Or use the skill:"
        echo "   /universal-compliance-report"
        ;;
    *)
        echo ""
        echo "Policy creation for '$FRAMEWORK' is not yet available."
        echo ""
        echo "Currently supported:"
        echo "  - pci-dss (PCI-DSS 4.0)"
        echo ""
        echo "Would you like to create policies for PCI-DSS? (y/n)"
        read CONFIRM
        if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
            python3 create_pci_dss_policies.py
        fi
        ;;
esac
```
