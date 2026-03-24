# Universal Compliance Reporting for RHACS
## Support for Any Compliance Framework

This guide explains how to use the universal compliance reporting tool that supports **any compliance framework** including NIST 800-190, NIST 800-53, PCI-DSS, HIPAA, CIS, GDPR, SOC 2, ISO 27001, FedRAMP, and custom frameworks.

---

## Overview

The universal compliance reporting tool provides a **framework-agnostic** approach to compliance reporting in RHACS. Instead of being hardcoded for NIST 800-190, it can generate reports for any compliance standard.

### Key Features

- ✅ **Multi-Framework Support**: NIST 800-190, NIST 800-53, PCI-DSS, HIPAA, CIS, GDPR, SOC 2, ISO 27001, FedRAMP
- ✅ **Custom Frameworks**: Define your own compliance frameworks
- ✅ **Flexible Policy Mapping**: Multiple ways to map policies to frameworks
- ✅ **Consistent Reporting**: Same report format across all frameworks
- ✅ **Easy Configuration**: YAML-based framework definitions

---

## Quick Start

### 1. List Available Frameworks

```bash
python3 universal_compliance_report.py --list
```

Output:
```
AVAILABLE COMPLIANCE FRAMEWORKS
================================================================================

ID: nist-800-190
  Name: NIST 800-190
  Full Name: NIST Special Publication 800-190 - Application Container Security Guide
  Description: Guidelines for container security
  Filter: name_prefix = NIST-800-190

ID: nist-800-53
  Name: NIST 800-53
  Full Name: NIST Special Publication 800-53 - Security and Privacy Controls
  Description: Security and privacy controls for information systems
  Filter: category = NIST 800-53

ID: pci-dss
  Name: PCI-DSS
  Full Name: Payment Card Industry Data Security Standard
  Description: Information security standard for organizations handling credit cards
  Filter: category = PCI

...
```

### 2. Generate a Report

```bash
# NIST 800-190 report
python3 universal_compliance_report.py --framework nist-800-190

# PCI-DSS report
python3 universal_compliance_report.py --framework pci-dss

# NIST 800-53 report
python3 universal_compliance_report.py --framework nist-800-53

# HIPAA report
python3 universal_compliance_report.py --framework hipaa
```

### 3. Output

The tool generates:
- Console output with detailed compliance status
- JSON file: `{framework-id}_compliance_report_YYYYMMDD_HHMMSS.json`

---

## Supported Frameworks

### Built-in Frameworks

| Framework ID | Name | Description |
|--------------|------|-------------|
| `nist-800-190` | NIST 800-190 | Application Container Security Guide |
| `nist-800-53` | NIST 800-53 | Security and Privacy Controls for Information Systems |
| `pci-dss` | PCI-DSS | Payment Card Industry Data Security Standard |
| `hipaa` | HIPAA | Health Insurance Portability and Accountability Act |
| `cis-kubernetes` | CIS Kubernetes | CIS Kubernetes Benchmark |
| `gdpr` | GDPR | General Data Protection Regulation |
| `soc2` | SOC 2 | Service Organization Control 2 |
| `iso-27001` | ISO 27001 | Information Security Management |
| `fedramp` | FedRAMP | Federal Risk and Authorization Management Program |

### Framework Details

#### NIST 800-190
```yaml
policy_filter:
  type: name_prefix
  value: NIST-800-190

categories:
  - 4.1 - Image Risks
  - 4.2 - Registry Risks
  - 4.3 - Orchestrator Risks
  - 4.4 - Container Risks
  - 4.5 - Host OS Risks
  - Runtime
```

#### NIST 800-53
```yaml
policy_filter:
  type: category
  value: NIST 800-53

categories:
  - Access Control (AC)
  - Audit and Accountability (AU)
  - Configuration Management (CM)
  - Identification and Authentication (IA)
  - System and Communications Protection (SC)
  - System and Information Integrity (SI)
```

#### PCI-DSS
```yaml
policy_filter:
  type: category
  value: PCI

categories:
  - Requirement 1 - Network Security
  - Requirement 2 - System Configuration
  - Requirement 3 - Data Protection
  - Requirement 4 - Data Transmission
  - Requirement 5 - Malware Protection
  - Requirement 6 - Secure Systems
  - Requirement 7 - Access Control
  - Requirement 8 - Authentication
  - Requirement 9 - Physical Access
  - Requirement 10 - Monitoring
  - Requirement 11 - Security Testing
  - Requirement 12 - Security Policy
```

---

## Configuration

### Framework Configuration File

Frameworks are defined in `compliance_frameworks.yaml`:

```yaml
frameworks:
  my-framework:
    name: "My Framework"
    full_name: "My Custom Compliance Framework"
    description: "Description of the framework"
    url: "https://example.com/framework"
    policy_filter:
      type: "category"  # or name_prefix, name_contains, tag
      value: "MY-FRAMEWORK"
    categories:
      - "Category 1"
      - "Category 2"
```

### Policy Filter Types

The `policy_filter` determines how RHACS policies are matched to the framework:

#### 1. **Category Filter**
```yaml
policy_filter:
  type: category
  value: "PCI"
```
Matches policies with category "PCI"

#### 2. **Name Prefix Filter**
```yaml
policy_filter:
  type: name_prefix
  value: "NIST-800-190"
```
Matches policies whose name starts with "NIST-800-190"

#### 3. **Name Contains Filter**
```yaml
policy_filter:
  type: name_contains
  value: "encryption"
```
Matches policies containing "encryption" in the name

#### 4. **Tag Filter**
```yaml
policy_filter:
  type: tag
  value: "compliance:soc2"
```
Matches policies with specific tag

---

## Creating Custom Frameworks

### Step 1: Define Your Framework

Create or edit `compliance_frameworks.yaml`:

```yaml
frameworks:
  my-custom-standard:
    name: "My Custom Standard"
    full_name: "My Organization's Security Standard v2.0"
    description: "Internal security and compliance requirements"
    url: "https://intranet.myorg.com/security-standards"
    policy_filter:
      type: "category"
      value: "CUSTOM-STANDARD"
    categories:
      - "Identity and Access"
      - "Data Protection"
      - "Network Security"
      - "Incident Response"
      - "Compliance and Audit"
```

### Step 2: Tag RHACS Policies

In RHACS, ensure your policies have the appropriate category or tags:

**Option A: Use Categories**
- In RHACS UI, edit each policy
- Add category: "CUSTOM-STANDARD"

**Option B: Use Tags**
- Tag policies with: `compliance:my-custom-standard`
- Update filter type to `tag` in YAML

**Option C: Use Naming Convention**
- Name policies: "CUSTOM-STANDARD-001", "CUSTOM-STANDARD-002", etc.
- Use `name_prefix` filter

### Step 3: Generate Report

```bash
python3 universal_compliance_report.py --framework my-custom-standard
```

---

## Advanced Usage

### Multiple Frameworks

Generate reports for multiple frameworks:

```bash
#!/bin/bash
# Generate all compliance reports

for framework in nist-800-190 nist-800-53 pci-dss hipaa cis-kubernetes
do
  echo "Generating $framework report..."
  python3 universal_compliance_report.py --framework $framework
done
```

### Custom Configuration File

Use a different configuration file:

```bash
python3 universal_compliance_report.py \
  --framework my-framework \
  --config /path/to/custom_frameworks.yaml
```

### Scheduled Reporting

Create a cron job for automated reports:

```bash
# Edit crontab
crontab -e

# Run PCI-DSS report weekly on Monday at 9 AM
0 9 * * 1 cd /path/to/compliance_reporting && python3 universal_compliance_report.py --framework pci-dss

# Run all frameworks monthly on 1st at midnight
0 0 1 * * cd /path/to/compliance_reporting && ./generate_all_reports.sh
```

---

## Report Output Format

### Console Output

```
================================================================================
RHACS Compliance Report - PCI-DSS
Generated: 2026-03-24 10:30:45
================================================================================

Fetching PCI-DSS policies...
Found 15 PCI-DSS policies
Found 520 deployments

Analyzing policy violations for PCI-DSS...
  Checking policy: PCI-DSS-Req-1-Network-Segmentation
  Checking policy: PCI-DSS-Req-2-Secure-Configuration
  ...

================================================================================
COMPLIANCE REPORT BY CLUSTER/NAMESPACE/DEPLOYMENT - PCI-DSS
================================================================================

################################################################################
CLUSTER: production-cluster
################################################################################

  Namespace: payment-processing
  ----------------------------------------------------------------------------

    Deployment: payment-api
      Summary: 12/15 policies PASS, 3/15 policies FAIL

      Failed Policies:
        ❌ PCI-DSS-Req-3-Data-Encryption
        ❌ PCI-DSS-Req-7-Access-Control
        ❌ PCI-DSS-Req-8-Authentication
```

### JSON Output

```json
{
  "framework": {
    "id": "pci-dss",
    "name": "PCI-DSS",
    "full_name": "Payment Card Industry Data Security Standard",
    "description": "Information security standard for organizations handling credit cards",
    "url": "https://www.pcisecuritystandards.org/"
  },
  "generated": "2026-03-24T10:30:45.123456",
  "policies": [
    {
      "id": "policy-uuid-1",
      "name": "PCI-DSS-Req-1-Network-Segmentation"
    },
    ...
  ],
  "compliance_data": {
    "production-cluster": {
      "payment-processing": {
        "payment-api": {
          "PCI-DSS-Req-1-Network-Segmentation": {
            "status": "PASS",
            "policy_id": "policy-uuid-1"
          },
          ...
        }
      }
    }
  }
}
```

---

## Integration with Existing Tools

### Use with Original NIST 800-190 Tool

The universal tool is compatible with the original NIST 800-190 tool:

```bash
# Old way (NIST 800-190 only)
python3 nist_compliance_report.py

# New way (any framework, including NIST 800-190)
python3 universal_compliance_report.py --framework nist-800-190
```

Both produce similar output for NIST 800-190.

### CSV and HTML Reports

Create universal versions:

```bash
# Generate CSV reports for any framework
python3 universal_csv_report.py --framework pci-dss

# Generate HTML dashboard for any framework
python3 universal_html_dashboard.py --framework hipaa
```

---

## Policy Mapping Best Practices

### 1. Consistent Naming Convention

Use consistent prefixes:
```
NIST-800-190-4.1.1-...
NIST-800-53-AC-1-...
PCI-DSS-Req-1-...
HIPAA-ADMIN-1-...
```

### 2. Category Organization

Organize policies by framework in RHACS:
- Create category: "NIST 800-53"
- Create category: "PCI-DSS"
- Create category: "HIPAA"

### 3. Multiple Framework Support

A single policy can belong to multiple frameworks:
- Categories: ["NIST 800-53", "PCI-DSS", "FedRAMP"]
- Tags: ["compliance:nist", "compliance:pci", "compliance:fedramp"]

### 4. Policy Descriptions

Include framework references in policy descriptions:
```
Policy Name: Encryption in Transit
Description: Ensures all data transmission uses TLS 1.2+
Frameworks: NIST 800-53 (SC-8), PCI-DSS (Req 4), HIPAA (164.312)
```

---

## Troubleshooting

### No Policies Found

**Problem**: `No policies found for {framework}`

**Solution**:
1. Check if policies exist in RHACS with the correct category/name/tag
2. Verify the filter configuration in `compliance_frameworks.yaml`
3. Test the API query manually:
   ```bash
   curl -H "Authorization: Bearer $RHACS_API_TOKEN" \
     "https://rhacs.example.com/v1/policies?query=Category:PCI"
   ```

### Wrong Policies Matched

**Problem**: Policies from other frameworks are included

**Solution**:
1. Make filter more specific (use `name_prefix` instead of `name_contains`)
2. Use unique category names
3. Review policy naming conventions

### Framework Not Found

**Problem**: `ERROR: Unknown framework: my-framework`

**Solution**:
1. Check framework ID spelling
2. Verify framework exists in YAML file
3. Use `--list` to see available frameworks

---

## Migration Guide

### Migrating from NIST 800-190 Tool

If you're currently using the NIST 800-190-specific tool:

**Before:**
```bash
python3 nist_compliance_report.py
python3 generate_csv_report.py
python3 generate_html_dashboard.py
```

**After:**
```bash
python3 universal_compliance_report.py --framework nist-800-190
python3 universal_csv_report.py --framework nist-800-190
python3 universal_html_dashboard.py --framework nist-800-190
```

**Or** keep using the old tools alongside new ones - they're compatible!

---

## Example Workflows

### Multi-Framework Audit

Generate reports for all required frameworks:

```bash
#!/bin/bash
# multi_framework_audit.sh

frameworks=(
  "nist-800-53"
  "pci-dss"
  "hipaa"
  "soc2"
)

for framework in "${frameworks[@]}"
do
  echo "===================="
  echo "Generating $framework report"
  echo "===================="

  python3 universal_compliance_report.py --framework $framework
  python3 universal_csv_report.py --framework $framework
  python3 universal_html_dashboard.py --framework $framework
done

echo "All compliance reports generated!"
```

### Framework Comparison

Compare compliance across different frameworks:

```bash
# Generate all reports
./multi_framework_audit.sh

# Create comparison summary
python3 -c "
import json
import glob

for file in glob.glob('*_compliance_report_*.json'):
    with open(file) as f:
        data = json.load(f)
        framework = data['framework']['name']
        total_policies = len(data['policies'])
        print(f'{framework}: {total_policies} policies')
"
```

---

## Future Enhancements

Planned features for universal compliance reporting:

- [ ] **Compliance Dashboard**: Multi-framework overview dashboard
- [ ] **Trend Analysis**: Track compliance over time across frameworks
- [ ] **Gap Analysis**: Compare compliance between frameworks
- [ ] **Mapping Table**: Show how policies map to multiple frameworks
- [ ] **Policy Recommendations**: Suggest policies for framework coverage
- [ ] **API Integration**: RESTful API for compliance data
- [ ] **Alerting**: Notify on compliance threshold violations
- [ ] **Executive Reports**: PDF reports with charts and graphs

---

## Support

### Documentation
- This guide: `UNIVERSAL_COMPLIANCE_GUIDE.md`
- Framework config: `compliance_frameworks.yaml`
- Main README: `README.md`

### Getting Help
- Check framework configuration with `--list`
- Review RHACS policy categories and names
- Verify API connectivity and permissions
- Check generated JSON output for details

---

## Summary

The universal compliance reporting tool provides:

✅ **Flexibility**: Support any compliance framework
✅ **Extensibility**: Easy to add custom frameworks
✅ **Consistency**: Same reporting format across frameworks
✅ **Compatibility**: Works alongside existing tools
✅ **Simplicity**: YAML configuration, no code changes needed

**Start using it today to generate compliance reports for any standard!**

```bash
python3 universal_compliance_report.py --framework pci-dss
```
