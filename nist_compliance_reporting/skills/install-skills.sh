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
echo "║   NIST Compliance Reporting - Claude Code Skills Installer    ║"
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
echo "  /setup-nist-reporting     - Set up RHACS credentials and environment"
echo "  /nist-compliance-report   - Generate full compliance report with guidance"
echo "  /quick-nist-report        - Quick report generation (all formats)"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "  1. In Claude Code, run: /setup-nist-reporting"
echo "  2. Configure your RHACS credentials"
echo "  3. Generate reports: /nist-compliance-report"
echo ""
echo "📖 For more information, see SKILLS_GUIDE.md"
echo ""
