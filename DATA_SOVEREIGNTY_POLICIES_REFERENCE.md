# Data Sovereignty Policies - Quick Reference

## Overview
15 comprehensive RHACS policies designed to enforce geographic data residency and regulatory compliance.

## Policy Summary Table

| Policy ID | Name | Severity | Lifecycle | Enforcement | Purpose |
|-----------|------|----------|-----------|-------------|---------|
| DS-1 | Enforce Geographic Node Placement (EU) | CRITICAL | DEPLOY | ✓ | Ensure EU workloads run only on EU nodes |
| DS-2 | Enforce Geographic Node Placement (US) | CRITICAL | DEPLOY | ✓ | Ensure US workloads run only on US nodes |
| DS-3 | Prevent Cross-Region Data Transfer | HIGH | DEPLOY | ✓ | Block unauthorized cross-region data flows |
| DS-4 | Restrict Container Registry to Approved Regions | HIGH | BUILD, DEPLOY | ✓ | Allow only regional registries |
| DS-5 | Enforce Data Classification Labels | MEDIUM | DEPLOY | - | Require data classification labels |
| DS-6 | Prevent Multi-Region PVCs | HIGH | DEPLOY | ✓ | Block multi-region storage |
| DS-7 | Detect Unauthorized Cloud API Access | HIGH | RUNTIME | ✓ | Monitor cloud provider API calls |
| DS-8 | Prevent External DNS Resolution | MEDIUM | RUNTIME | - | Detect DNS queries to external domains |
| DS-9 | Restrict Data Export Tools | HIGH | BUILD, DEPLOY | ✓ | Block data export utilities |
| DS-10 | Enforce Regional Encryption Keys | HIGH | DEPLOY | - | Require region-specific KMS keys |
| DS-11 | Require Geo-Fencing Annotations | MEDIUM | DEPLOY | - | Mandate geo-fence annotations |
| DS-12 | Detect Unauthorized Database Connections | CRITICAL | RUNTIME | ✓ | Monitor database connections |
| DS-13 | Prevent Cross-Border Service Mesh Traffic | HIGH | DEPLOY | ✓ | Block service mesh cross-region routing |
| DS-14 | Audit Log Export to Regional Storage | MEDIUM | DEPLOY | - | Ensure logs stay in region |
| DS-15 | Enforce Data Residency for Backups | CRITICAL | DEPLOY | ✓ | Lock backups to approved regions |

## Policies by Category

### 1. Node Placement & Scheduling (DS-1, DS-2)
**What they do**: Prevent workloads from running on nodes outside approved regions

**Required labels**:
- Workload: `data-classification: eu-regulated` or `us-regulated`
- Node: `topology.kubernetes.io/region: eu-*` or `us-*`

**Example violation**:
```yaml
# Pod labeled eu-regulated but no node selector for EU
metadata:
  labels:
    data-classification: eu-regulated
spec:
  containers: [...]  # Missing nodeSelector or affinity
```

**Remediation**:
```yaml
spec:
  nodeSelector:
    topology.kubernetes.io/region: eu-west-1
```

### 2. Cross-Region Transfer Prevention (DS-3, DS-7, DS-12)
**What they do**: Detect and block data transfers across geographic boundaries

**Triggers**:
- Environment variables with cross-region endpoints
- Runtime processes accessing foreign cloud APIs
- Database connections to non-regional hosts

**Example violation**:
```yaml
env:
- name: DATABASE_URL
  value: "postgres://db.us-east-1.aws.com"  # US endpoint in EU workload
```

**Remediation**:
```yaml
env:
- name: DATABASE_URL
  value: "postgres://db.eu-west-1.aws.com"  # Regional endpoint
```

### 3. Registry & Supply Chain (DS-4, DS-9)
**What they do**: Ensure images come from approved regional sources

**Approved registries** (customize in policy):
- `eu.gcr.io`
- `*.eu.*.ecr.amazonaws.com`
- `registry.eu-west-1.redhat.io`

**Example violation**:
```yaml
containers:
- image: us.gcr.io/my-project/app:v1  # US registry for EU workload
```

**Remediation**:
```yaml
containers:
- image: eu.gcr.io/my-project/app:v1  # EU registry
```

### 4. Storage & Persistence (DS-6, DS-10, DS-15)
**What they do**: Ensure data at rest remains in approved regions

**Requirements**:
- Use regional storage classes
- Regional KMS encryption keys
- Regional backup destinations

**Example violation**:
```yaml
storageClassName: multi-region-storage  # Replicates across regions
```

**Remediation**:
```yaml
storageClassName: regional-storage-eu  # Single region only
```

### 5. Service Mesh & Networking (DS-13, DS-8)
**What they do**: Prevent service mesh misconfigurations that route traffic across regions

**Required configuration**:
- Locality-based load balancing
- Failover within same region only
- Restrict DNS queries

**Example Istio config**:
```yaml
trafficPolicy:
  loadBalancer:
    localityLbSetting:
      enabled: true
      failover:
      - from: eu-west-1
        to: eu-central-1  # EU only
```

### 6. Compliance & Labeling (DS-5, DS-11)
**What they do**: Enforce proper labeling for compliance tracking

**Required labels/annotations**:
```yaml
metadata:
  labels:
    data-classification: eu-regulated|us-regulated|confidential
  annotations:
    geo-fence.region: eu-west|us-west
    allowed-regions: eu-west-1,eu-central-1
    data-residency: eu
```

### 7. Logging & Auditing (DS-14)
**What they do**: Ensure audit logs remain within regional boundaries

**Example compliant config**:
```yaml
env:
- name: LOG_ENDPOINT
  value: "logs.eu-west-1.internal"
- name: SYSLOG_HOST
  value: "syslog.eu-region.company.com"
```

## Implementation Checklist

### Pre-Deployment
- [ ] Review and customize `data_sovereignty_policies.json` for your regions
- [ ] Label all cluster nodes with region information
- [ ] Create regional storage classes
- [ ] Configure regional container registries
- [ ] Set up regional KMS keys

### Cluster Configuration
- [ ] Label nodes: `kubectl label nodes <name> topology.kubernetes.io/region=eu-west-1`
- [ ] Create namespaces with data classification labels
- [ ] Configure network policies for egress control
- [ ] Set up service mesh locality routing (if using Istio/Linkerd)

### Workload Configuration
- [ ] Add `data-classification` labels to all deployments
- [ ] Add `geo-fence` annotations
- [ ] Configure node selectors or affinity rules
- [ ] Use regional registries for all images
- [ ] Set regional endpoints in environment variables
- [ ] Use regional storage classes for PVCs
- [ ] Configure regional backup destinations

### Testing
- [ ] Deploy test workloads with incorrect labels (should fail)
- [ ] Attempt to use non-regional registries (should fail)
- [ ] Try cross-region PVC (should fail)
- [ ] Test runtime detection with curl to foreign endpoints
- [ ] Verify logs stay in region

### Monitoring
- [ ] Configure RHACS notifiers for policy violations
- [ ] Set up alerting for data sovereignty breaches
- [ ] Create dashboards for compliance tracking
- [ ] Schedule regular policy reviews

## Common Violations & Fixes

### Violation 1: Missing Node Selector
**Error**: "Deployment data-classification=eu-regulated without EU node selector"

**Fix**:
```yaml
spec:
  template:
    spec:
      nodeSelector:
        topology.kubernetes.io/region: eu-west-1
```

### Violation 2: Non-Regional Registry
**Error**: "Image from unapproved registry"

**Fix**: Change image from `us.gcr.io/project/app` to `eu.gcr.io/project/app`

### Violation 3: Cross-Region Environment Variable
**Error**: "Environment variable points to non-regional endpoint"

**Fix**:
```yaml
# Before
- name: DB_HOST
  value: "db.us-east-1.aws.com"

# After
- name: DB_HOST
  value: "db.eu-west-1.aws.com"
```

### Violation 4: Missing Data Classification Label
**Error**: "Deployment missing required data-classification label"

**Fix**:
```yaml
metadata:
  labels:
    data-classification: eu-regulated
```

### Violation 5: Multi-Region Storage
**Error**: "PVC uses multi-region storage class"

**Fix**: Change `storageClassName` from `multi-region` to `regional-storage-eu`

## Policy Customization Guide

### Adding New Regions
Edit `data_sovereignty_policies.json`:

```json
{
  "name": "Data-Sovereignty-X - Enforce Geographic Node Placement (Asia-Pacific)",
  "policySections": [{
    "policyGroups": [{
      "fieldName": "Required Label",
      "values": [{"value": "data-classification=apac-regulated"}]
    }, {
      "fieldName": "Required Node Label",
      "values": [{"value": "topology.kubernetes.io/region=ap-.*"}]
    }]
  }]
}
```

### Adjusting Severity Levels
Change severity based on risk tolerance:
- `CRITICAL_SEVERITY`: Strict enforcement, blocks deployments
- `HIGH_SEVERITY`: Important controls, strong enforcement
- `MEDIUM_SEVERITY`: Advisory, may not block
- `LOW_SEVERITY`: Informational

### Adding Registry Allowlists
Update DS-4 policy:
```json
"values": [
  {"value": "eu.gcr.io"},
  {"value": "registry.eu-west-1.company.com"},
  {"value": ".*\\.eu\\..*"}
]
```

### Creating Exclusions
In RHACS UI or via API:
```json
"exclusions": [{
  "name": "Exclude system namespaces",
  "deployment": {
    "scope": {
      "namespace": "kube-system"
    }
  }
}]
```

## Regulatory Mapping

| Policy | GDPR | CCPA | LGPD | PIPEDA | APPI |
|--------|------|------|------|--------|------|
| DS-1, DS-2 | ✓ | ✓ | ✓ | ✓ | ✓ |
| DS-3 | ✓ | ✓ | ✓ | ✓ | ✓ |
| DS-4 | ✓ | ✓ | ✓ | - | ✓ |
| DS-6 | ✓ | ✓ | ✓ | ✓ | ✓ |
| DS-7, DS-12 | ✓ | ✓ | ✓ | - | ✓ |
| DS-15 | ✓ | ✓ | ✓ | ✓ | ✓ |

## Quick Commands

```bash
# Deploy all data sovereignty policies
python3 data_sovereignty_policy_creator.py

# Label nodes with region
kubectl label nodes --all topology.kubernetes.io/region=eu-west-1

# Label namespace
kubectl label namespace production data-classification=eu-regulated

# Check policy violations in RHACS
roxctl -e $ROX_CENTRAL policy list --categories "Data Sovereignty"

# Test deployment compliance
kubectl apply -f my-deployment.yaml --dry-run=server

# View node labels
kubectl get nodes --show-labels | grep topology

# Check workload labels
kubectl get deployments -A -o custom-columns=NAME:.metadata.name,CLASSIFICATION:.metadata.labels.data-classification
```

## Troubleshooting

### Issue: Policies not triggering
**Solution**:
1. Check if policy is enabled in RHACS UI
2. Verify label exists on workload
3. Confirm node labels are correct
4. Review policy scope and exclusions

### Issue: Too many false positives
**Solution**:
1. Start with enforcement disabled
2. Add appropriate exclusions
3. Refine regex patterns in policies
4. Adjust severity levels

### Issue: Can't deploy legitimate workload
**Solution**:
1. Check all required labels are present
2. Verify node selector matches node labels
3. Ensure using approved registries
4. Review policy violation details in RHACS

## Further Reading

- Complete guide: `DATA_SOVEREIGNTY_GUIDE.md`
- Example configurations: `examples_data_sovereignty.yaml`
- Main documentation: `README.md`
- RHACS docs: https://docs.openshift.com/acs/

## Support

For policy customization help, refer to:
1. `DATA_SOVEREIGNTY_GUIDE.md` - Comprehensive implementation guide
2. `examples_data_sovereignty.yaml` - Working configuration examples
3. RHACS documentation - Platform-specific guidance

