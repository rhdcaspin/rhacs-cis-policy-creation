#!/bin/bash
#
# Install NIST Compliance Reporting Skills for Claude Code
#
# This script copies the skill files to Claude Code's skills directory
# so they can be invoked with slash commands like /nist-compliance-report
#

set -e

SKILLS_DIR="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Compliance Reporting - Claude Code Skills Installer         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Create skills directory if it doesn't exist
if [ ! -d "$SKILLS_DIR" ]; then
    echo "📁 Creating Claude Code skills directory: $SKILLS_DIR"
    mkdir -p "$SKILLS_DIR"
else
    echo "✓ Skills directory exists: $SKILLS_DIR"
fi

echo ""
echo "📦 Installing skills..."
echo ""

# Copy each skill file
skills=(
    "setup-nist-reporting.md"
    "nist-compliance-report.md"
    "quick-nist-report.md"
    "universal-compliance-report.md"
    "create-compliance-policies.md"
    "quick-compliance-setup.md"
)

for skill in "${skills[@]}"; do
    if [ -f "$SCRIPT_DIR/$skill" ]; then
        cp "$SCRIPT_DIR/$skill" "$SKILLS_DIR/"
        echo "  ✓ Installed: $skill"
    else
        echo "  ✗ Not found: $skill"
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Installation Complete!                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 Available Skills:"
echo ""
echo "NIST 800-190 Specific:"
echo "  /setup-nist-reporting       - Set up RHACS credentials and environment"
echo "  /nist-compliance-report     - Generate NIST 800-190 compliance report"
echo "  /quick-nist-report          - Quick NIST report generation (all formats)"
echo ""
echo "Universal (Any Framework):"
echo "  /universal-compliance-report - Generate reports for any framework"
echo "  /create-compliance-policies  - Create policies in RHACS"
echo "  /quick-compliance-setup      - Complete setup: policies + reports"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "For NIST 800-190:"
echo "  1. Run: /setup-nist-reporting"
echo "  2. Generate: /quick-nist-report"
echo ""
echo "For Any Framework (PCI-DSS, HIPAA, etc):"
echo "  1. Run: /quick-compliance-setup"
echo "  2. Select framework (e.g., pci-dss)"
echo ""
echo "📖 For more information, see SKILLS_GUIDE.md"
echo ""
