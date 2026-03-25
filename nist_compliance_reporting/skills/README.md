# Claude Code Skills for RHACS Compliance Reporting

Slash-command skills for generating compliance reports from Red Hat Advanced Cluster Security (RHACS). All skills call the RHACS REST API directly — no external scripts or dependencies required beyond `curl` and `python3`.

## Prerequisites

- `curl` and `python3` available in your shell
- A running RHACS instance
- An RHACS API token (Admin or Analyst role)
- Environment variables set:
  ```bash
  export RHACS_URL='https://your-rhacs-instance.com'
  export RHACS_API_TOKEN='your-api-token'
  ```

## Installation

Copy the skill files to your Claude Code skills directory:

```bash
cp *.md ~/.claude/skills/
```

Then restart Claude Code (or open a new session) and the skills will be available.

## Available Skills

### `/setup-nist-reporting`

Initial setup: configure credentials, verify RHACS connectivity, and confirm NIST 800-190 data is available.

### `/nist-compliance-report`

Full guided NIST 800-190 report: checks connectivity, fetches compliance results and active violations, and provides a summary with recommendations.

### `/quick-nist-report`

Fast one-liner: pulls NIST 800-190 compliance rate and active alert count in seconds.

### `/universal-compliance-report`

Report for any built-in RHACS compliance standard:
- NIST SP 800-190
- NIST SP 800-53 Rev 4
- PCI DSS 3.2
- HIPAA §164
- CIS Kubernetes v1.5
- CIS Docker v1.2

### `/create-compliance-policies`

Create framework-specific policies in RHACS via the API. Currently supports PCI-DSS 4.0 (5 core policies). Uses `POST /v1/policies`.

### `/quick-compliance-setup`

End-to-end workflow: choose a framework, optionally create policies, trigger a compliance scan, and display results.

## How Skills Work

Each skill is a markdown prompt that instructs Claude to:
1. Verify environment variables (`RHACS_URL`, `RHACS_API_TOKEN`)
2. Call the RHACS REST API with `curl`
3. Parse JSON responses with inline `python3`
4. Display a formatted compliance summary with recommendations

No Python scripts, no project directories, no extra dependencies — just the RHACS API.

## Key API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/metadata` | Verify connectivity |
| `GET /v1/compliance/runresults` | Compliance control results |
| `GET /v1/alerts?query=Category:X` | Active policy violations |
| `GET /v1/alertscount` | Count of active alerts |
| `POST /v1/compliancemanagement/triggerruns` | Trigger a compliance scan |
| `POST /v1/policies` | Create a policy |

## Troubleshooting

**Skills not appearing?**
1. Verify installation: `ls ~/.claude/skills/*.md`
2. Restart Claude Code

**Empty compliance results?**
- No scan has run for that framework yet
- Trigger one in RHACS: Compliance > Scan
- Or use `/quick-compliance-setup` which triggers a scan automatically

**401 Unauthorized?**
- Check `RHACS_API_TOKEN` is set and not expired
- Generate a new token in RHACS: Platform Configuration > Integrations > API Token

**SSL errors?**
- Add `-k` to curl commands if using self-signed certificates
- Set a custom CA if required by your organization
