# Claude Code Skills for NIST Compliance Reporting

This directory contains Claude Code skills that provide slash command shortcuts for NIST 800-190 compliance reporting.

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

### `/setup-nist-reporting`
**Purpose**: Initial setup and configuration

Sets up RHACS credentials, environment variables, and verifies dependencies.

### `/nist-compliance-report`
**Purpose**: Full guided report generation

Generates all reports with detailed feedback, summaries, and recommendations.

### `/quick-nist-report`
**Purpose**: Fast report generation

Quickly generates all reports and opens the HTML dashboard.

## Usage

After installation, open Claude Code and type:

```
/setup-nist-reporting
```

Claude will guide you through the setup process.

Then generate reports:

```
/nist-compliance-report
```

Or for quick reports:

```
/quick-nist-report
```

## Skill Files

- `setup-nist-reporting.md` - Setup and configuration workflow
- `nist-compliance-report.md` - Full guided report generation
- `quick-nist-report.md` - Quick report generation
- `install-skills.sh` - Installation script

## Documentation

For detailed documentation, see:
- `../SKILLS_GUIDE.md` - Complete skills guide
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
