# Quick NIST Report

Generate a concise NIST 800-190 violation summary from RHACS in one shot.

---

You are generating a quick NIST 800-190 compliance summary from RHACS.

## Quick Execution

### 1. Verify environment

```bash
[ -z "$RHACS_URL" ] && echo "ERROR: RHACS_URL not set" && exit 1
[ -z "$RHACS_API_TOKEN" ] && echo "ERROR: RHACS_API_TOKEN not set" && exit 1
CURL_OPTS="-s"
[ "${RHACS_VERIFY_SSL}" = "false" ] && CURL_OPTS="$CURL_OPTS -k"
echo "Environment OK"
```

### 2. Pull NIST violation count and top issue

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/alerts?query=Category%3ANIST&pagination.limit=500" \
  | python3 -c "
import sys, json

d = json.load(sys.stdin)
alerts = d.get('alerts', [])

by_policy = {}
by_sev = {}
for a in alerts:
    pol = a.get('policy', {})
    name = pol.get('name', 'unknown')
    sev = pol.get('severity', 'UNKNOWN').replace('_SEVERITY', '')
    by_policy[name] = by_policy.get(name, 0) + 1
    by_sev[sev] = by_sev.get(sev, 0) + 1

worst = max(by_policy, key=by_policy.get) if by_policy else 'none'
critical = by_sev.get('CRITICAL', 0)
high = by_sev.get('HIGH', 0)

print(f'NIST 800-190 | {len(alerts)} violations | {critical} critical / {high} high | top: {worst}')
"
```

### 3. Pull total NIST policy count

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/policies?query=Category%3ANIST" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'NIST policies configured: {len(d.get(\"policies\", []))}')
"
```

If errors occur, run `/nist-compliance-report` for the full guided experience.
