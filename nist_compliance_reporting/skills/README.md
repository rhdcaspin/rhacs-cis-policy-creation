# Claude Code Skills for Compliance Reporting

This directory contains Claude Code skills that provide slash command shortcuts for multi-framework compliance reporting in RHACS.

## What are Skills?

Skills are reusable prompts in Claude Code that can be invoked with slash commands (e.g., `/commit`, `/review-pr`). They provide specialized workflows for common tasks.

## Quick Installation

```bash
# From the skills directory
./install-skills.sh
```

Or manually:

```bash
# Copy skills to Claude Code directory
cp *.md ~/.claude/skills/
```

## Available Skills

### Universal Skills (Any Framework)

#### `/quick-compliance-setup` ⭐
**Purpose**: Complete compliance setup workflow

One-command setup for any framework:
- Creates policies in RHACS (PCI-DSS supported)
- Generates JSON, CSV, and HTML reports
- Opens dashboard in browser

**Frameworks**: PCI-DSS, NIST 800-190, NIST 800-53, HIPAA, CIS, GDPR, SOC 2, ISO 27001, FedRAMP

#### `/universal-compliance-report`
**Purpose**: Generate reports for any framework

Interactive report generation:
- Lists available frameworks
- Generates all report formats
- Displays summary statistics

#### `/create-compliance-policies`
**Purpose**: Create compliance policies in RHACS

Creates framework-specific policies:
- PCI-DSS 4.0 (15 policies)
- More frameworks coming soon

### NIST 800-190 Specific Skills

#### `/setup-nist-reporting`
**Purpose**: Initial NIST 800-190 setup

Sets up RHACS credentials, environment variables, and verifies dependencies.

#### `/nist-compliance-report`
**Purpose**: Full guided NIST report generation

Generates NIST 800-190 reports with detailed feedback, summaries, and recommendations.

#### `/quick-nist-report`
**Purpose**: Fast NIST report generation

Quickly generates all NIST 800-190 reports and opens the HTML dashboard.

## Usage

### Quick Start (Any Framework)

For complete setup with policy creation and reporting:

```
/quick-compliance-setup
```

Then select your framework (e.g., `pci-dss`, `hipaa`, `nist-800-190`).

### Generate Reports Only

For existing policies:

```
/universal-compliance-report
```

### NIST 800-190 Workflow

Initial setup:

```
/setup-nist-reporting
```

Generate reports:

```
/quick-nist-report
```

### Create Policies

To create compliance policies in RHACS:

```
/create-compliance-policies
```

## Skill Files

**Universal Skills:**
- `quick-compliance-setup.md` - Complete setup: policies + reports
- `universal-compliance-report.md` - Multi-framework report generation
- `create-compliance-policies.md` - Policy creation workflow

**NIST 800-190 Skills:**
- `setup-nist-reporting.md` - NIST setup and configuration
- `nist-compliance-report.md` - Full NIST guided report generation
- `quick-nist-report.md` - Quick NIST report generation

**Utilities:**
- `install-skills.sh` - Installation script
- `README.md` - This file

## Documentation

For detailed documentation, see:
- `../UNIVERSAL_COMPLIANCE_GUIDE.md` - Multi-framework usage guide
- `../SKILLS_GUIDE.md` - Complete skills guide (NIST 800-190)
- `../README.md` - Main project documentation
- `../QUICK_START.md` - Quick reference

## Troubleshooting

### Skills not appearing?

1. Verify installation:
```bash
ls -la ~/.claude/skills/nist*.md
```

2. Restart Claude Code

3. Type `/nist` and press Tab to see available skills

### Skills not working?

1. Check you're in the correct directory (project root)
2. Verify environment variables are set
3. Run `/setup-nist-reporting` to reconfigure

## Contributing

To create custom skills:

1. Create a new `.md` file in this directory
2. Follow the format of existing skills
3. Test thoroughly
4. Submit a PR

## Support

- Read the skills guide: `../SKILLS_GUIDE.md`
- Check main README: `../README.md`
- Open an issue on GitHub
