# Claude Code Skills for NIST Compliance Reporting

This guide explains how to use the Claude Code skills for NIST 800-190 compliance reporting.

## What are Skills?

Skills are reusable prompts in Claude Code that can be invoked with slash commands (like `/commit` or `/review-pr`). They provide specialized capabilities for common tasks.

## Available Skills

Three skills have been created for NIST compliance reporting:

### 1. `/setup-nist-reporting` - Initial Setup
**Purpose**: Guide you through the complete setup process

**What it does**:
- Checks if project directory exists
- Creates `.env` configuration file
- Helps you configure RHACS credentials
- Verifies Python dependencies
- Tests the connection
- Provides security reminders

**When to use**:
- First time setting up the tool
- Setting up on a new machine
- Troubleshooting configuration issues

**Example**:
```
/setup-nist-reporting
```

### 2. `/nist-compliance-report` - Full Guided Report
**Purpose**: Generate comprehensive compliance reports with guidance

**What it does**:
- Verifies prerequisites (directory, env vars, dependencies)
- Runs console report + JSON export
- Generates CSV reports (3 files)
- Creates HTML dashboard
- Provides summary of key findings
- Lists generated files
- Suggests next steps
- Handles errors gracefully

**When to use**:
- First time running reports
- When you want detailed feedback
- When troubleshooting issues
- For comprehensive analysis

**Example**:
```
/nist-compliance-report
```

### 3. `/quick-nist-report` - Fast Report Generation
**Purpose**: Quickly generate all reports without extra guidance

**What it does**:
- Runs all three report generators in sequence
- Opens HTML dashboard automatically
- Provides one-line summary
- Minimal output, maximum speed

**When to use**:
- Regular/scheduled reporting
- When environment is already configured
- When you need results quickly
- For automated workflows

**Example**:
```
/quick-nist-report
```

## Installation

The skills are automatically installed when you clone this repository. They are located in:

```
~/.claude/skills/
├── setup-nist-reporting.md
├── nist-compliance-report.md
└── quick-nist-report.md
```

### Manual Installation

If you need to install manually:

1. Create the skills directory:
```bash
mkdir -p ~/.claude/skills
```

2. Copy the skill files from this repository:
```bash
cp /path/to/this/repo/nist_compliance_reporting/skills/*.md ~/.claude/skills/
```

Or create them manually using the templates in this guide.

## Usage Examples

### First Time Setup
```
User: /setup-nist-reporting

Claude will guide you through:
1. ✓ Checking project directory
2. ✓ Creating .env file
3. ✓ Getting RHACS credentials
4. ✓ Setting environment variables
5. ✓ Installing dependencies
6. ✓ Verifying connection
```

### Generate Full Report
```
User: /nist-compliance-report

Claude will:
1. Check prerequisites
2. Run all report generators
3. Show summary statistics
4. List generated files
5. Provide recommendations
```

### Quick Daily Report
```
User: /quick-nist-report

Claude will:
1. Run all reports silently
2. Open HTML dashboard
3. Show one-line summary: "518 deployments, 65% compliant, top issue: Root User (233 violations)"
```

## Workflow Examples

### New User Workflow
```bash
# 1. Clone the repository
git clone https://github.com/rhdcaspin/rhacs-cis-policy-creation.git
cd rhacs-cis-policy-creation

# 2. Open Claude Code and run setup
/setup-nist-reporting

# 3. Generate first report
/nist-compliance-report

# 4. Future reports
/quick-nist-report
```

### Scheduled Reporting Workflow
```bash
# In Claude Code, run daily/weekly
/quick-nist-report

# Review the HTML dashboard
# Compare with previous reports
# Track compliance trends
```

### Troubleshooting Workflow
```bash
# If quick report fails
/nist-compliance-report

# If that fails, reconfigure
/setup-nist-reporting
```

## Skill Arguments

Currently, these skills don't accept arguments. Future versions may support:

```bash
# Potential future enhancements
/nist-compliance-report --cluster production
/quick-nist-report --format csv
/setup-nist-reporting --env production
```

## Creating Your Own Skills

You can create custom skills for specific needs:

### Example: Policy-Specific Report Skill

Create `~/.claude/skills/nist-root-user-report.md`:

```markdown
# NIST Root User Report

Focus on root user violations only.

---

Generate a focused report on NIST-800-190-4.1.4 Root User in Container violations.

1. Navigate to nist_compliance_reporting/
2. Run the full report
3. Extract and highlight root user violations specifically
4. Provide remediation suggestions for this specific policy
5. Show example Kubernetes securityContext configurations
```

### Example: Export to S3 Skill

Create `~/.claude/skills/nist-report-to-s3.md`:

```markdown
# NIST Report to S3

Generate reports and upload to S3.

---

1. Generate all reports using /quick-nist-report
2. Upload the latest reports to S3:
   - nist_compliance_dashboard_*.html
   - nist_compliance_summary_*.csv
3. Set appropriate S3 permissions
4. Generate presigned URLs for sharing
5. Notify user of upload completion
```

## Best Practices

### 1. Start with Setup
Always run `/setup-nist-reporting` when:
- Setting up on a new machine
- Onboarding new team members
- Troubleshooting configuration

### 2. Use Full Report Initially
Run `/nist-compliance-report` for:
- First-time users learning the tool
- Understanding what each output file contains
- Diagnosing issues

### 3. Switch to Quick for Regular Use
Use `/quick-nist-report` for:
- Daily/weekly reporting
- Automated workflows
- Quick status checks

### 4. Combine with Other Skills
```bash
# Generate report and commit
/quick-nist-report
/commit  # Commit the generated reports

# Generate report and create PR
/nist-compliance-report
/create-pr  # Create PR with compliance updates
```

## Troubleshooting Skills

### Skill Not Found
If you see "skill not found":

1. Check skill files exist:
```bash
ls ~/.claude/skills/nist*.md
```

2. Verify file format (should be .md)

3. Restart Claude Code

4. Check skill name matches exactly:
   - `/nist-compliance-report` ✓
   - `/nist_compliance_report` ✗
   - `/nist-report` ✗

### Skill Not Working as Expected

1. Read the skill file to understand what it does:
```bash
cat ~/.claude/skills/nist-compliance-report.md
```

2. Verify environment variables are set

3. Check you're in the correct directory

4. Try running the underlying Python scripts manually first

## Advanced: Skill Composition

You can create meta-skills that call other skills:

Create `~/.claude/skills/weekly-compliance-workflow.md`:

```markdown
# Weekly Compliance Workflow

Complete weekly compliance workflow.

---

Execute the weekly compliance reporting workflow:

1. Run /quick-nist-report to generate fresh reports
2. Compare with last week's reports to identify trends
3. Summarize changes in compliance rates
4. Identify new violations and resolved issues
5. Generate executive summary with key metrics
6. Suggest action items for team
```

## Tips and Tricks

1. **Tab Completion**: Type `/nist` and press Tab to see available NIST skills

2. **Help Text**: Skills include their description in the first line

3. **Combine with CLI**: Skills can use any command-line tools

4. **Chain Skills**: Output from one skill can inform the next

5. **Context Aware**: Skills have access to your current directory and environment

## Contributing

To contribute new skills:

1. Create skill file in `~/.claude/skills/`
2. Follow the markdown format (title, description, content)
3. Test thoroughly
4. Submit PR to add to this guide
5. Share with the community

## Support

For issues or questions:
- Check this guide
- Review the skill file content
- Read the main README.md
- Check QUICK_START.md
- Open an issue on GitHub

---

**Next Steps**: Try running `/setup-nist-reporting` to get started!
