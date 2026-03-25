# Quick Compliance Setup

Discover all active compliance violations across every framework configured in RHACS.

---

You are running a complete compliance violation overview for the user.

## Step 1: Verify Environment

```bash
[ -z "$RHACS_URL" ] && echo "ERROR: RHACS_URL not set" && exit 1
[ -z "$RHACS_API_TOKEN" ] && echo "ERROR: RHACS_API_TOKEN not set" && exit 1
CURL_OPTS="-s"
[ "${RHACS_VERIFY_SSL}" = "false" ] && CURL_OPTS="$CURL_OPTS -k"
echo "Environment OK — $RHACS_URL"
```

## Step 2: Discover All Policy Categories

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/alerts?pagination.limit=500" \
  | python3 -c "
import sys, json

d = json.load(sys.stdin)
alerts = d.get('alerts', [])

categories = set()
for a in alerts:
    for cat in a.get('policy', {}).get('categories', []):
        categories.add(cat)

print('Active alert categories in this environment:')
for cat in sorted(categories):
    print(f'  - {cat}')
print()
print(f'Total active alerts: {len(alerts)}')
"
```

Ask the user which category/framework they want to focus on, or proceed with the full overview below.

## Step 3: Full Violation Overview

```bash
curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/alerts?pagination.limit=500" \
  | python3 -c "
import sys, json

d = json.load(sys.stdin)
alerts = d.get('alerts', [])

print('Compliance Violation Overview')
print('=' * 60)
print(f'Total active violations: {len(alerts)}')
print()

by_cat = {}
by_sev = {}
namespaces = set()

for a in alerts:
    pol = a.get('policy', {})
    sev = pol.get('severity', 'UNKNOWN').replace('_SEVERITY', '')
    ns = a.get('commonEntityInfo', {}).get('namespace', 'unknown')
    by_sev[sev] = by_sev.get(sev, 0) + 1
    namespaces.add(ns)
    for cat in pol.get('categories', ['Uncategorized']):
        if cat not in by_cat:
            by_cat[cat] = {'count': 0, 'policies': set()}
        by_cat[cat]['count'] += 1
        by_cat[cat]['policies'].add(pol.get('name', 'unknown'))

print('Severity breakdown:')
for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    cnt = by_sev.get(sev, 0)
    if cnt:
        print(f'  {sev:10s}: {cnt}')
print(f'  Namespaces affected: {len(namespaces)}')
print()
print('Violations by framework/category:')
for cat, info in sorted(by_cat.items(), key=lambda x: -x[1]['count']):
    print(f'  {info[\"count\"]:4d} violations  |  {len(info[\"policies\"]):2d} policies  |  {cat}')
"
```

## Step 4: Drill Down by Framework

Ask the user which framework to drill into, then run:

```bash
CATEGORY="PCI"  # Replace with user's choice

ENCODED_CATEGORY="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$CATEGORY")"

curl $CURL_OPTS \
  -H "Authorization: Bearer $RHACS_API_TOKEN" \
  "$RHACS_URL/v1/alerts?query=Category%3A${ENCODED_CATEGORY}&pagination.limit=500" \
  | CATEGORY="$CATEGORY" python3 -c "
import sys, json, os

d = json.load(sys.stdin)
alerts = d.get('alerts', [])
cat = os.environ['CATEGORY']

print(f'{cat} Violations Detail')
print('=' * 60)

by_policy = {}
by_sev = {}
for a in alerts:
    pol = a.get('policy', {})
    name = pol.get('name', 'unknown')
    sev = pol.get('severity', 'UNKNOWN').replace('_SEVERITY', '')
    by_policy[name] = by_policy.get(name, 0) + 1
    by_sev[sev] = by_sev.get(sev, 0) + 1

print(f'Total: {len(alerts)}')
for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    cnt = by_sev.get(sev, 0)
    if cnt:
        print(f'  {sev}: {cnt}')
print()
print('Top policies:')
for name, cnt in sorted(by_policy.items(), key=lambda x: -x[1])[:10]:
    print(f'  {cnt:3d}x  {name}')
"
```

## Step 5: Summary

After displaying results, provide:
1. Overall compliance posture across all frameworks
2. The highest-risk framework (most critical/high violations)
3. Top 3 specific remediations
4. Console link: `$RHACS_URL/main/violations`

## Error Handling

- **401** → `RHACS_API_TOKEN` is invalid or expired
- **Connection error** → verify `RHACS_URL` is correct and reachable
