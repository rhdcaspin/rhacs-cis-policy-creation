# RHACS Data Sovereignty Policy Guide

## Overview

This guide covers the implementation and deployment of Red Hat Advanced Cluster Security (RHACS) policies specifically designed to enforce **data sovereignty** and **geographic data residency** requirements.

Data sovereignty refers to the concept that data is subject to the laws and governance structures of the nation or region where it is collected or stored. These policies help organizations comply with various international data protection regulations.

## Regulatory Compliance

These policies help address requirements from:

- **GDPR** (General Data Protection Regulation) - European Union
- **CCPA** (California Consumer Privacy Act) - United States
- **LGPD** (Lei Geral de Proteção de Dados) - Brazil
- **PIPEDA** (Personal Information Protection and Electronic Documents Act) - Canada
- **APPI** (Act on Protection of Personal Information) - Japan
- **DPA** (Data Protection Act) - United Kingdom
- Other regional and industry-specific regulations

## Policy Categories

### 1. Geographic Node Placement Policies

**Purpose**: Ensure workloads are scheduled only on nodes within approved geographic regions.

**Policies**:
- `Data-Sovereignty-1` - Enforce Geographic Node Placement (EU Region)
- `Data-Sovereignty-2` - Enforce Geographic Node Placement (US Region)

**Requirements**:
- Nodes must be labeled with region information:
  ```yaml
  topology.kubernetes.io/region: eu-west-1
  topology.kubernetes.io/zone: eu-west-1a
  ```
- Workloads must be labeled with data classification:
  ```yaml
  labels:
    data-classification: eu-regulated
  ```

**Example Pod Configuration**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: eu-data-processor
  labels:
    data-classification: eu-regulated
spec:
  nodeSelector:
    topology.kubernetes.io/region: eu-west-1
  # or use node affinity
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: topology.kubernetes.io/region
            operator: In
            values:
            - eu-west-1
            - eu-central-1
  containers:
  - name: app
    image: myapp:latest
```

### 2. Cross-Region Data Transfer Prevention

**Purpose**: Prevent unauthorized data transfer across geographic boundaries.

**Policies**:
- `Data-Sovereignty-3` - Prevent Cross-Region Data Transfer
- `Data-Sovereignty-7` - Detect Unauthorized Cloud Provider API Access
- `Data-Sovereignty-12` - Detect Unauthorized Database Connections

**Best Practices**:
- Use internal service endpoints that are region-locked
- Implement network policies to restrict egress traffic
- Configure service mesh with locality-aware routing

**Example Network Policy**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-external-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      data-classification: eu-regulated
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          region: eu
    ports:
    - protocol: TCP
      port: 443
  - to:
    - podSelector: {}  # Allow intra-namespace
```

### 3. Registry and Supply Chain Controls

**Purpose**: Ensure container images are sourced only from approved regional registries.

**Policies**:
- `Data-Sovereignty-4` - Restrict Container Registry to Approved Regions
- `Data-Sovereignty-9` - Restrict Data Export Tools

**Approved Registry Configuration**:
```yaml
# Example for EU-based deployments
spec:
  containers:
  - name: app
    image: eu.gcr.io/my-project/app:v1.0.0  # EU-specific registry
    # NOT: us.gcr.io/my-project/app:v1.0.0  # Would violate policy
```

**Registry Allowlist Configuration** (in RHACS):
- Navigate to: Platform Configuration → Registries
- Add approved regional registries:
  - `eu.gcr.io/*`
  - `*.dkr.ecr.eu-west-1.amazonaws.com/*`
  - `registry.eu-west-1.redhat.io/*`

### 4. Storage and Data Persistence

**Purpose**: Ensure data at rest remains within approved geographic boundaries.

**Policies**:
- `Data-Sovereignty-6` - Prevent Multi-Region Persistent Volume Claims
- `Data-Sovereignty-10` - Enforce Encryption at Rest with Regional Keys

**Storage Class Configuration**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: regional-storage-eu
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:eu-west-1:123456789:key/abcd-1234"
allowedTopologies:
- matchLabelExpressions:
  - key: topology.kubernetes.io/zone
    values:
    - eu-west-1a
    - eu-west-1b
    - eu-west-1c
volumeBindingMode: WaitForFirstConsumer
```

**PVC Configuration**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc-regional
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: regional-storage-eu
  resources:
    requests:
      storage: 10Gi
```

### 5. Backup and Disaster Recovery

**Purpose**: Ensure backups maintain data within sovereignty boundaries.

**Policies**:
- `Data-Sovereignty-15` - Enforce Data Residency for Backup Services

**Velero Configuration Example**:
```yaml
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: eu-backup-location
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: eu-backups-bucket
  config:
    region: eu-west-1
    s3ForcePathStyle: "true"
---
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: eu-workload-backup
  namespace: velero
spec:
  includedNamespaces:
  - eu-production
  storageLocation: eu-backup-location
  labelSelector:
    matchLabels:
      data-classification: eu-regulated
```

### 6. Service Mesh and Traffic Management

**Purpose**: Prevent service mesh misconfigurations that route traffic across regions.

**Policies**:
- `Data-Sovereignty-13` - Prevent Cross-Border Service Mesh Traffic

**Istio Configuration Example**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: locality-aware-routing
spec:
  host: myservice.production.svc.cluster.local
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
    loadBalancer:
      localityLbSetting:
        enabled: true
        failover:
        - from: eu-west-1
          to: eu-central-1  # Only failover within EU
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

### 7. Logging and Audit Controls

**Purpose**: Ensure audit logs remain within approved regions.

**Policies**:
- `Data-Sovereignty-14` - Audit Log Export to Regional Storage Only

**Fluentd Configuration Example**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: logging
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      tag kubernetes.*
    </source>
    
    <match **>
      @type s3
      s3_bucket eu-logs-bucket
      s3_region eu-west-1
      path logs/
      store_as gzip
      <buffer>
        @type file
        path /var/log/fluent/s3
        timekey 3600
        timekey_wait 10m
      </buffer>
    </match>
```

## Deployment Instructions

### Prerequisites

1. **RHACS Central** installed and accessible
2. **API Token** with policy management permissions
3. **Configuration file** (`config.json`) properly configured

### Step 1: Configure RHACS Connection

Create or update `config.json`:
```json
{
  "rhacs": {
    "central_url": "https://your-rhacs-central.example.com:443",
    "api_token": "your-api-token-here"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
  },
  "policies": {
    "config_file": "data_sovereignty_policies.json",
    "skip_existing": true
  }
}
```

### Step 2: Customize Policy Values

Edit `data_sovereignty_policies.json` to match your environment:

1. **Update region labels** to match your cluster:
   ```json
   "values": [
     {
       "value": "topology.kubernetes.io/region=eu-.*"
     }
   ]
   ```

2. **Update registry allowlists**:
   ```json
   "values": [
     {
       "value": "eu.gcr.io"
     },
     {
       "value": "your-regional-registry.com"
     }
   ]
   ```

3. **Adjust severity levels** based on your risk tolerance

### Step 3: Deploy Policies

#### Option 1: Deploy All Data Sovereignty Policies
```bash
python3 data_sovereignty_policy_creator.py
```

#### Option 2: Deploy All Policies (Including CIS)
```bash
python3 rhacs_cis_policy_creator.py
```

#### Option 3: Dry Run (Test Mode)
```bash
# Modify script to skip actual creation and just validate
python3 data_sovereignty_policy_creator.py --dry-run
```

### Step 4: Verify Deployment

1. Log into RHACS Central UI
2. Navigate to **Platform Configuration → Policy Management**
3. Filter by "Data-Sovereignty" to see created policies
4. Review and enable/disable as needed

## Cluster Configuration Requirements

### Node Labels

Ensure all nodes are properly labeled with geographic information:

```bash
# AWS EKS (automatic)
kubectl get nodes --show-labels | grep topology

# Manual labeling
kubectl label nodes node-1 topology.kubernetes.io/region=eu-west-1
kubectl label nodes node-1 topology.kubernetes.io/zone=eu-west-1a
kubectl label nodes node-1 region=eu
```

### Namespace Labels

Label namespaces to indicate data classification:

```bash
kubectl label namespace production data-classification=eu-regulated
kubectl label namespace production geo-fence.region=eu-west
```

### Workload Labels

Add labels to deployments and pods:

```yaml
metadata:
  labels:
    data-classification: eu-regulated
    data-residency: eu-west-1
  annotations:
    geo-fence.region: eu-west
    allowed-regions: eu-west-1,eu-central-1
```

## Testing and Validation

### Test 1: Verify Node Placement Enforcement

```yaml
# This should PASS if node has EU label
apiVersion: v1
kind: Pod
metadata:
  name: test-eu-pass
  labels:
    data-classification: eu-regulated
spec:
  nodeSelector:
    topology.kubernetes.io/region: eu-west-1
  containers:
  - name: nginx
    image: nginx:latest
```

```yaml
# This should FAIL (no EU node selector)
apiVersion: v1
kind: Pod
metadata:
  name: test-eu-fail
  labels:
    data-classification: eu-regulated
spec:
  containers:
  - name: nginx
    image: nginx:latest
```

### Test 2: Verify Registry Restrictions

```bash
# Should PASS (EU registry)
kubectl run test-eu-registry --image=eu.gcr.io/my-project/app:v1

# Should FAIL (US registry)
kubectl run test-us-registry --image=us.gcr.io/my-project/app:v1
```

### Test 3: Runtime Detection

Deploy a test pod and attempt prohibited actions:

```bash
# Should trigger runtime alert
kubectl exec -it test-pod -- curl https://s3.us-west-2.amazonaws.com
```

## Exclusions and Exceptions

Some system workloads may need exclusions:

1. **In RHACS UI**: Navigate to policy → Add Exclusion
2. **Scope Options**:
   - Namespace: `kube-system`, `openshift-*`
   - Label: `app=monitoring`
   - Deployment: `cluster-critical-app`

**Example JSON exclusion**:
```json
"exclusions": [
  {
    "name": "Exclude monitoring namespace",
    "deployment": {
      "scope": {
        "namespace": "monitoring"
      }
    }
  }
]
```

## Monitoring and Alerting

### Configure Notifiers

1. **Email Notifications**:
```json
{
  "name": "Data Sovereignty Alerts",
  "type": "email",
  "labelKey": "data-classification",
  "labelValue": ".*-regulated",
  "email": {
    "server": "smtp.company.com",
    "sender": "rhacs-alerts@company.com",
    "recipients": ["security-team@company.com"]
  }
}
```

2. **Slack Integration**:
```json
{
  "name": "Data Sovereignty Slack",
  "type": "slack",
  "slack": {
    "webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

### Dashboard Queries

**Violations by Region**:
```sql
SELECT 
  policy_name,
  cluster_name,
  namespace,
  deployment_name,
  COUNT(*) as violations
FROM violations
WHERE policy_name LIKE 'Data-Sovereignty%'
GROUP BY cluster_name, namespace
ORDER BY violations DESC
```

## Troubleshooting

### Common Issues

1. **Policy Not Triggering**
   - Verify labels exist on workloads
   - Check policy scope and exclusions
   - Ensure enforcement is enabled

2. **False Positives**
   - Review regex patterns in policy
   - Add appropriate exclusions
   - Adjust severity to avoid blocking legitimate traffic

3. **Node Selector Failures**
   - Verify node labels are correct
   - Check node affinity rules
   - Ensure nodes exist in required regions

### Debug Commands

```bash
# Check node labels
kubectl get nodes -o json | jq '.items[].metadata.labels'

# Check pod labels
kubectl get pods -A -o json | jq '.items[].metadata.labels'

# View RHACS policy violations
roxctl -e "$ROX_CENTRAL" policy list --categories "Data Sovereignty"

# Check specific deployment compliance
roxctl -e "$ROX_CENTRAL" deployment check --deployment <name>
```

## Best Practices

1. **Start with Report-Only Mode**
   - Deploy policies with enforcement disabled initially
   - Monitor for false positives
   - Gradually enable enforcement

2. **Use Layered Controls**
   - Combine RHACS policies with network policies
   - Implement IAM controls at cloud provider level
   - Use service mesh for additional traffic controls

3. **Regular Audits**
   - Review policy violations weekly
   - Update policies as regulations change
   - Test disaster recovery procedures

4. **Documentation**
   - Document approved regions and registries
   - Maintain exemption records
   - Create runbooks for incidents

5. **Team Training**
   - Educate developers on data sovereignty requirements
   - Provide policy documentation
   - Establish approval processes for exceptions

## Additional Resources

- [RHACS Documentation](https://docs.openshift.com/acs/)
- [Kubernetes Topology Labels](https://kubernetes.io/docs/reference/labels-annotations-taints/)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [Data Residency Best Practices](https://www.redhat.com/en/topics/security/data-residency)

## Support and Contributions

For issues, questions, or contributions:
- Review existing policies in `data_sovereignty_policies.json`
- Modify policies to match your specific requirements
- Test thoroughly in non-production environments
- Submit feedback or improvements

## License

These policies are provided as examples for educational and compliance purposes. Customize according to your organization's specific requirements and regulatory obligations.

