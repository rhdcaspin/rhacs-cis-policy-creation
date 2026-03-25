# Create Compliance Policies

Create compliance policies in RHACS for a chosen framework via the RHACS API.

---

You are creating compliance policies in RHACS by calling the RHACS REST API directly.

## Step 1: Verify Environment

```bash
[ -z "$RHACS_URL" ] && echo "ERROR: RHACS_URL not set" && exit 1
[ -z "$RHACS_API_TOKEN" ] && echo "ERROR: RHACS_API_TOKEN not set" && exit 1
CURL_OPTS="-s"
[ "${RHACS_VERIFY_SSL}" = "false" ] && CURL_OPTS="$CURL_OPTS -k"
echo "Environment OK"
```

## Step 2: Choose Framework

Ask the user which framework to create policies for. Currently supported:

- **PCI-DSS 4.0** — Payment Card Industry Data Security Standard (15 policies)

More frameworks can be added by following the same pattern below.

## Step 3: Create Policies via API

For each policy, POST a JSON payload to `$RHACS_URL/v1/policies`.

### Policy JSON Structure

```json
{
  "name": "Policy Name",
  "description": "What this policy checks",
  "rationale": "Why this control matters",
  "remediation": "Steps to fix violations",
  "categories": ["PCI-DSS"],
  "lifecycleStages": ["DEPLOY"],
  "severity": "HIGH_SEVERITY",
  "policyVersion": "1.1",
  "policySections": [
    {
      "sectionName": "Section 1",
      "policyGroups": [
        {
          "fieldName": "Privileged Container",
          "booleanOperator": "OR",
          "values": [{"value": "true"}]
        }
      ]
    }
  ]
}
```

### Helper Function

Use this shell function to create a policy and report status:

```bash
create_policy() {
  local NAME="$1"
  local JSON="$2"
  local RESULT
  RESULT=$(curl $CURL_OPTS -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $RHACS_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$JSON" \
    "$RHACS_URL/v1/policies")
  local HTTP_CODE
  HTTP_CODE=$(echo "$RESULT" | tail -1)
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "  [OK] $NAME"
  else
    echo "  [SKIP] $NAME (HTTP $HTTP_CODE — may already exist)"
  fi
}
```

### PCI-DSS 4.0 Core Policies

Create the following policies by calling `create_policy` for each:

```bash
echo "Creating PCI-DSS 4.0 policies..."

# PCI-DSS Req 2.2.1 — No privileged containers
create_policy "PCI-DSS: No Privileged Containers" '{
  "name": "PCI-DSS: No Privileged Containers",
  "description": "Privileged containers are prohibited under PCI-DSS requirement 2.2.1",
  "rationale": "Privileged containers bypass host security controls and expand the attack surface",
  "remediation": "Remove privileged: true from container security context",
  "categories": ["PCI-DSS"],
  "lifecycleStages": ["DEPLOY"],
  "severity": "HIGH_SEVERITY",
  "policyVersion": "1.1",
  "policySections": [{"sectionName": "Section 1","policyGroups": [{"fieldName": "Privileged Container","booleanOperator": "OR","values": [{"value": "true"}]}]}]
}'

# PCI-DSS Req 6.3.3 — No images with critical CVEs
create_policy "PCI-DSS: No Critical CVEs in Images" '{
  "name": "PCI-DSS: No Critical CVEs in Images",
  "description": "Images with critical vulnerabilities violate PCI-DSS requirement 6.3.3",
  "rationale": "Unpatched critical CVEs expose cardholder data environments to known exploits",
  "remediation": "Update base images and application dependencies to patched versions",
  "categories": ["PCI-DSS"],
  "lifecycleStages": ["DEPLOY","BUILD"],
  "severity": "CRITICAL_SEVERITY",
  "policyVersion": "1.1",
  "policySections": [{"sectionName": "Section 1","policyGroups": [{"fieldName": "Image Scan Age","booleanOperator": "OR","values": [{"value": "30"}]},{"fieldName": "Fixed By","booleanOperator": "OR","values": [{"value": ".*"}]}]}]
}'

# PCI-DSS Req 8.2 — No default credentials
create_policy "PCI-DSS: No Default Credentials" '{
  "name": "PCI-DSS: No Default Credentials",
  "description": "Default or empty passwords prohibited under PCI-DSS requirement 8.2",
  "rationale": "Default credentials are trivially exploited by attackers",
  "remediation": "Remove default credentials; use secrets management (Vault, k8s Secrets)",
  "categories": ["PCI-DSS"],
  "lifecycleStages": ["DEPLOY"],
  "severity": "HIGH_SEVERITY",
  "policyVersion": "1.1",
  "policySections": [{"sectionName": "Section 1","policyGroups": [{"fieldName": "Environment Variable","booleanOperator": "OR","values": [{"value": "(?i)password=.+"}]}]}]
}'

# PCI-DSS Req 1.3 — No host network access
create_policy "PCI-DSS: No Host Network Access" '{
  "name": "PCI-DSS: No Host Network Access",
  "description": "Host network access violates PCI-DSS network segmentation (Requirement 1.3)",
  "rationale": "Host networking bypasses pod-level network isolation",
  "remediation": "Set hostNetwork: false in pod spec",
  "categories": ["PCI-DSS"],
  "lifecycleStages": ["DEPLOY"],
  "severity": "HIGH_SEVERITY",
  "policyVersion": "1.1",
  "policySections": [{"sectionName": "Section 1","policyGroups": [{"fieldName": "Host Network","booleanOperator": "OR","values": [{"value": "true"}]}]}]
}'

# PCI-DSS Req 10.2 — No write access to host filesystem
create_policy "PCI-DSS: No Writable Host Filesystem" '{
  "name": "PCI-DSS: No Writable Host Filesystem",
  "description": "Writable host filesystem mounts violate PCI-DSS audit log integrity (Req 10.2)",
  "rationale": "Writable host mounts allow tampering with audit logs and system files",
  "remediation": "Remove host path mounts or mount read-only",
  "categories": ["PCI-DSS"],
  "lifecycleStages": ["DEPLOY"],
  "severity": "HIGH_SEVERITY",
  "policyVersion": "1.1",
  "policySections": [{"sectionName": "Section 1","policyGroups": [{"fieldName": "Writable Host Mount","booleanOperator": "OR","values": [{"value": "true"}]}]}]
}'

echo ""
echo "PCI-DSS policy creation complete."
echo "View policies: $RHACS_URL/main/policies"
```

## Step 4: Next Steps

After creating policies, recommend:

1. Run a compliance scan in RHACS (Compliance > Scan)
2. Use `/universal-compliance-report` to generate a report
3. Review violations in the RHACS console under Violations

## Error Handling

- **HTTP 409 Conflict** → policy already exists (safe to ignore)
- **HTTP 401** → check `RHACS_API_TOKEN`
- **HTTP 400 Bad Request** → policy JSON is malformed; check field names against your RHACS version
