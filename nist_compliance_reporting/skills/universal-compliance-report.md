# Universal Compliance Report Generator

Generate a violation report for any compliance framework configured in RHACS.

---

You are generating a compliance violation report from RHACS for a user-selected framework.

## Supported Frameworks

Present this list and ask the user to choose:

| Framework | Category query (substring match) |
|-----------|----------------------------------|
| NIST 800-190 | `NIST` |
| PCI DSS | `PCI` |
| HIPAA | `HIPAA` |
| CIS Docker | `Docker CIS` |
| CIS Kubernetes | `Kubernetes` |
| SOC 2 | `SOC2` |

Note: RHACS does a substring match on policy categories, so `NIST` will match a category named `NIST 800-190`. If results are empty, check your exact policy category labels in RHACS under Policy Management and adjust the query accordingly.

## Step 1: Verify Environment

```bash
[ -z "$RHACS_URL" ] && echo "ERROR: RHACS_URL not set" && exit 1
[ -z "$RHACS_API_TOKEN" ] && echo "ERROR: RHACS_API_TOKEN not set" && exit 1
CURL_OPTS="-s"
[ "${RHACS_VERIFY_SSL}" = "false" ] && CURL_OPTS="$CURL_OPTS -k"
echo "Environment OK"
```

## Step 2: Fetch Policies for Selected Framework

Replace `CATEGORY` with the user's chosen category (e.g., `PCI`).

```bash
CATEGORY="PCI"  # Set to user's choice

ENCODED_CATEGORY="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$CATEGORY")"

curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/policies?query=Category%3A${ENCODED_CATEGORY}" \
  | CATEGORY="$CATEGORY" python3 -c "
import sys, json, os

d = json.load(sys.stdin)
policies = d.get('policies', [])
category = os.environ['CATEGORY']

print(f'{category} Policies Configured')
print('=' * 60)
print(f'Total policies: {len(policies)}')
by_sev = {}
for p in policies:
    sev = p.get('severity', 'UNKNOWN').replace('_SEVERITY', '')
    by_sev[sev] = by_sev.get(sev, 0) + 1
for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    cnt = by_sev.get(sev, 0)
    if cnt:
        print(f'  {sev}: {cnt} policies')

if not policies:
    print(f'No policies with category \"{category}\" found.')
    print('Check your policy categories in RHACS under Policy Management.')
"
```

## Step 3: Fetch Active Violations

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/alerts?query=Category%3A${ENCODED_CATEGORY}&pagination.limit=500" \
  | CATEGORY="$CATEGORY" python3 -c "
import sys, json, os

d = json.load(sys.stdin)
alerts = d.get('alerts', [])
category = os.environ['CATEGORY']

print()
print(f'{category} Active Violations')
print('=' * 60)
print(f'Total violations: {len(alerts)}')

by_policy = {}
by_sev = {}
namespaces = set()
clusters = set()

for a in alerts:
    pol = a.get('policy', {})
    name = pol.get('name', 'unknown')
    sev = pol.get('severity', 'UNKNOWN').replace('_SEVERITY', '')
    ns = a.get('commonEntityInfo', {}).get('namespace', 'unknown')
    cl = a.get('commonEntityInfo', {}).get('clusterName', 'unknown')
    by_policy[name] = by_policy.get(name, 0) + 1
    by_sev[sev] = by_sev.get(sev, 0) + 1
    namespaces.add(ns)
    clusters.add(cl)

print(f'Namespaces affected: {len(namespaces)}')
print(f'Clusters affected  : {len(clusters)}')
print()
print('Severity breakdown:')
for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    cnt = by_sev.get(sev, 0)
    if cnt:
        print(f'  {sev}: {cnt}')
print()
print('Top violating policies:')
for name, cnt in sorted(by_policy.items(), key=lambda x: -x[1])[:10]:
    print(f'  {cnt:3d}x  {name}')
"
```

## Step 4: Summary

After displaying results, provide:
1. A brief compliance posture summary
2. Top 3 violations with recommended remediation
3. Next steps (fix violations, re-run to verify, review RHACS console)

## Error Handling

- **Empty results** → no policies with that category exist; verify category label in RHACS
- **401** → check `RHACS_API_TOKEN`
- **Connection error** → verify `RHACS_URL`
