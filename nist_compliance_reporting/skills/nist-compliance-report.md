# NIST Compliance Report

Generate a NIST 800-190 compliance report from RHACS using policy violations.

---

You are tasked with generating a NIST 800-190 compliance report from RHACS.

## Step 1: Verify Environment

```bash
[ -z "$RHACS_URL" ] && echo "ERROR: RHACS_URL not set" && exit 1
[ -z "$RHACS_API_TOKEN" ] && echo "ERROR: RHACS_API_TOKEN not set" && exit 1
CURL_OPTS="-s"
[ "${RHACS_VERIFY_SSL}" = "false" ] && CURL_OPTS="$CURL_OPTS -k"
echo "Environment OK"
```

## Step 2: Test API Connectivity

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/metadata" \
  | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('Connected. RHACS version:', d.get('version', 'unknown'))
except Exception as e:
    print('ERROR: Could not connect:', e)
    sys.exit(1)
"
```

If this fails:
- **401 Unauthorized** → token is wrong or expired
- **Connection error** → check `RHACS_URL`
- **SSL error** → set `export RHACS_VERIFY_SSL=false` for self-signed certs (dev/test only)

## Step 3: Fetch NIST Policies

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/policies?query=Category%3ANIST" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
policies = d.get('policies', [])
print(f'NIST policies configured: {len(policies)}')
by_sev = {}
for p in policies:
    sev = p.get('severity', 'UNKNOWN').replace('_SEVERITY', '')
    by_sev[sev] = by_sev.get(sev, 0) + 1
for sev, cnt in sorted(by_sev.items()):
    print(f'  {sev}: {cnt}')
if not policies:
    print('No NIST-category policies found.')
    print('Create policies with Category=NIST in RHACS, or run /create-compliance-policies.')
"
```

## Step 4: Fetch Active NIST Violations

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/alerts?query=Category%3ANIST&pagination.limit=500" \
  | python3 -c "
import sys, json

d = json.load(sys.stdin)
alerts = d.get('alerts', [])

print()
print('NIST 800-190 Active Violations')
print('=' * 60)
print(f'Total active violations: {len(alerts)}')

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

if not alerts:
    print('No active NIST violations found.')
    print('Either all NIST policies are passing, or no NIST policies are configured.')
"
```

## Step 5: Summary and Recommendations

After displaying results, provide:
1. A brief executive summary (overall NIST compliance posture)
2. Top 3 violations with remediation guidance:
   - Privileged containers → remove `privileged: true` from pod specs
   - Host path mounts → remove or set `readOnly: true`
   - Missing resource limits → add `resources.limits` to containers
3. Next steps (fix violations, re-run `/nist-compliance-report` to verify)
