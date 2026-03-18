# Setup NIST Reporting

Set up environment for NIST 800-190 compliance reporting.

---

You are helping the user set up the NIST 800-190 compliance reporting tool.

## Setup Steps

### 1. Navigate to Project
- Check if `nist_compliance_reporting/` directory exists
- If in a different location, navigate to the correct directory

### 2. Configuration File
- Check if `.env` file exists in `nist_compliance_reporting/`
- If not, copy from template:
  ```bash
  cp nist_compliance_reporting/.env.example nist_compliance_reporting/.env
  ```

### 3. Get RHACS Credentials
Ask the user for:
- **RHACS URL**: The URL of their RHACS instance (e.g., https://rhacs.example.com)
- **API Token**: Their RHACS API token

Explain how to generate an API token:
1. Log in to RHACS web console
2. Go to Platform Configuration > Integrations
3. Click API Token
4. Create new token with Admin or Analyst role
5. Copy the generated token

### 4. Configure Environment
Help the user set environment variables:

**Option A - Export (session-based):**
```bash
export RHACS_URL='https://their-rhacs-instance.com'
export RHACS_API_TOKEN='their-api-token'
export RHACS_VERIFY_SSL=false  # or true for production
```

**Option B - .env file (persistent):**
Edit `nist_compliance_reporting/.env`:
```
RHACS_URL=https://their-rhacs-instance.com
RHACS_API_TOKEN=their-api-token
RHACS_VERIFY_SSL=false
```

Then load it:
```bash
set -a
source nist_compliance_reporting/.env
set +a
```

### 5. Install Dependencies
Check if Python packages are installed:
```bash
pip3 install requests urllib3
```

Or if using requirements.txt in parent directory:
```bash
pip3 install -r requirements.txt
```

### 6. Verify Setup
Test the connection:
```bash
cd nist_compliance_reporting
python3 -c "
import os
import sys
url = os.getenv('RHACS_URL')
token = os.getenv('RHACS_API_TOKEN')
if not url or not token:
    print('❌ Environment variables not set')
    sys.exit(1)
print('✅ Environment configured')
print(f'   URL: {url}')
print(f'   Token: {token[:20]}...')
"
```

### 7. Ready to Use
Once setup is complete, inform the user they can now:
- Run `/nist-compliance-report` for full guided reporting
- Run `/quick-nist-report` for fast report generation
- Run individual scripts manually

## Security Reminders
- Never commit `.env` file to git
- Keep API tokens secure
- Rotate tokens periodically
- Use `RHACS_VERIFY_SSL=true` in production

Present the setup in a clear, step-by-step format with checkboxes or numbered steps.
