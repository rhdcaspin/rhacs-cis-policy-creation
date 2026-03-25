# Setup NIST Reporting

Configure credentials and verify RHACS connectivity for NIST 800-190 compliance reporting.

---

You are helping the user set up their RHACS environment.

## Step 1: Get RHACS Credentials

Ask the user for:
- **RHACS URL**: The URL of their RHACS instance (e.g., `https://central.rhacs.example.com`)
- **API Token**: Their RHACS API token

How to generate an API token in RHACS:
1. Log in to the RHACS web console
2. Go to **Platform Configuration > Integrations**
3. Click **API Token**
4. Create a new token with **Admin** or **Analyst** role
5. Copy the generated token

## Step 2: Set Environment Variables

**Option A — Session only:**
```bash
export RHACS_URL='https://your-rhacs-instance.com'
export RHACS_API_TOKEN='your-api-token'
```

**Option B — Persistent (.env file, do NOT commit to git):**
```
RHACS_URL=https://your-rhacs-instance.com
RHACS_API_TOKEN=your-api-token
```
Load it:
```bash
set -a && source .env && set +a
```

## Step 3: Verify Connectivity

```bash
CURL_OPTS="-s"
[ "${RHACS_VERIFY_SSL}" = "false" ] && CURL_OPTS="$CURL_OPTS -k"

curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/metadata" \
  | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('Connected to RHACS')
    print('  Version:', d.get('version', 'unknown'))
    print('  License:', d.get('licenseStatus', 'unknown'))
except Exception as e:
    print('ERROR: Could not parse response:', e)
    sys.exit(1)
"
```

If this fails:
- **SSL error** → install the RHACS CA certificate into your system trust store, or set `export RHACS_VERIFY_SSL=false` for self-signed certs in dev/test environments only — never disable TLS verification in production
- **Connection refused** → verify `RHACS_URL` is correct and the instance is running
- **401 Unauthorized** → the token is wrong or expired

## Step 4: Verify NIST Policies Exist

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/policies?query=Category%3ANIST" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
policies = d.get('policies', [])
if policies:
    print(f'NIST policies found: {len(policies)}')
    for p in policies[:5]:
        print(f'  [{p.get(\"severity\",\"?\").replace(\"_SEVERITY\",\"\")}] {p.get(\"name\")}')
else:
    print('No NIST-category policies found.')
    print('Create policies with Category=NIST in RHACS Policy Management,')
    print('or run /create-compliance-policies to add them via the API.')
"
```

## Step 5: Ready to Use

Once setup is complete, the user can run:

- `/nist-compliance-report` — full guided report with violation details
- `/quick-nist-report` — fast one-line violation summary
- `/universal-compliance-report` — report for any framework

## Security Reminders

- Never commit `.env` files or tokens to git
- Rotate API tokens periodically
- Use HTTPS and valid TLS certificates in production
