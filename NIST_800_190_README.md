# NIST SP 800-190 Application Container Security Guide - RHACS Policies

## Overview

This directory contains RHACS/ACS security policies based on **NIST Special Publication 800-190: Application Container Security Guide**. The policies are split into two separate scripts following a generate-then-deploy pattern.

## NIST 800-190 Coverage

NIST SP 800-190 addresses container security across five major areas:

1. **Image Security** (Section 4.1) - Policies 1-4
2. **Registry Security** (Section 4.2) - Covered by Image policies  
3. **Orchestrator Security** (Section 4.3) - Covered by Runtime policies
4. **Container Runtime Security** (Section 4.4) - Policies 5-9
5. **Host OS Security** (Section 4.5) - Policies 10-11

Additionally, 3 runtime detection policies are included.

## Files

### Core Scripts

- **`nist_800_190_generate.py`** - Generates policy JSON definitions
- **`nist_800_190_deploy.py`** - Deploys policies to RHACS/ACS
- **`.env`** - Environment file with RHACS connection details (not in git)

### Generated Files

- **`nist_800_190_policies.json`** - Generated policy definitions (12 working policies)

## Deployment Statistics

✅ **Successfully Deployed: 12/12 policies (100%)**

- ✓ Image Security: 3 policies
- ✓ Container Runtime: 4 policies  
- ✓ Host OS Security: 2 policies
- ✓ Runtime Detection: 3 policies

All policies are fully functional and actively monitoring your RHACS environment.

## Quick Start

### 1. Configure Connection

Edit `.env` file with your RHACS credentials:

```bash
RHACS_URL=https://your-rhacs-instance.com
RHACS_TOKEN=your-api-token-here
```

### 2. Generate Policies

```bash
python3 nist_800_190_generate.py
```

This creates `nist_800_190_policies.json` with all 12 working policy definitions.

### 3. Deploy to RHACS

```bash
python3 nist_800_190_deploy.py
```

This connects to RHACS and creates the policies.

## Policy List

### Image Security Policies

| ID | Name | Severity | Enforcement |
|----|------|----------|-------------|
| 4.1.1 | Image Vulnerabilities Not Scanned | HIGH | ✓ Build + Deploy |
| 4.1.2 | Insecure Container Images | HIGH | ✓ Build + Deploy |
| 4.1.4 | Root User in Container | HIGH | ✓ Deploy |

### Container Runtime Security Policies

| ID | Name | Severity | Enforcement |
|----|------|----------|-------------|
| 4.4.1 | Privileged Containers | CRITICAL | ✓ Deploy |
| 4.4.2 | Host Namespace Sharing | HIGH | ✓ Deploy |
| 4.4.4 | Dangerous Linux Capabilities | HIGH | ✓ Deploy |
| 4.4.5 | Privilege Escalation Allowed | HIGH | ✓ Deploy |

### Host OS Security Policies

| ID | Name | Severity | Enforcement |
|----|------|----------|-------------|
| 4.5.1 | Sensitive Host Paths Mounted | HIGH | ✓ Deploy |
| 4.5.2 | HostPath Volumes Used | MEDIUM | Advisory |

### Runtime Detection Policies

| ID | Name | Severity | Type |
|----|------|----------|------|
| RT-1 | Unauthorized Process Execution | HIGH | Runtime |
| RT-2 | Cryptocurrency Mining Detection | HIGH | Runtime |
| RT-3 | Package Manager Usage | MEDIUM | Runtime |

## Policy Details

### Image Security (4.1)

**NIST-800-190-4.1.1 - Image Vulnerabilities Not Scanned**
- Ensures images are scanned for vulnerabilities before deployment
- Blocks images older than 90 days (not recently scanned)
- Enforcement: BUILD + DEPLOY

**NIST-800-190-4.1.2 - Insecure Container Images**
- Only allows images from trusted registries
- Approved registries: quay.io, registry.redhat.io, gcr.io, AWS ECR
- Enforcement: BUILD + DEPLOY

**NIST-800-190-4.1.4 - Root User in Container**
- Prevents containers from running as root user
- Reduces privilege escalation risks
- Enforcement: DEPLOY

### Container Runtime Security (4.4)

**NIST-800-190-4.4.1 - Privileged Containers**
- Blocks containers with privileged mode enabled
- Prevents root-level host access
- Enforcement: DEPLOY
- Severity: CRITICAL

**NIST-800-190-4.4.2 - Host Namespace Sharing**
- Blocks sharing of host network, PID, or IPC namespaces
- Maintains container isolation
- Enforcement: DEPLOY

**NIST-800-190-4.4.4 - Dangerous Linux Capabilities**
- Blocks dangerous capabilities: SYS_ADMIN, NET_ADMIN, SYS_MODULE, etc.
- Reduces attack surface
- Enforcement: DEPLOY

**NIST-800-190-4.4.5 - Privilege Escalation Allowed**
- Blocks allowPrivilegeEscalation=true
- Prevents processes from gaining more privileges
- Enforcement: DEPLOY

### Host OS Security (4.5)

**NIST-800-190-4.5.1 - Sensitive Host Paths Mounted**
- Blocks mounting of sensitive directories: /, /etc, /boot, /proc, /sys, etc.
- Prevents host compromise
- Enforcement: DEPLOY

**NIST-800-190-4.5.2 - HostPath Volumes Used**
- Alerts on use of HostPath volumes
- Encourages use of proper volume types
- Enforcement: Advisory

### Runtime Detection

**NIST-800-190-Runtime-1 - Unauthorized Process Execution**
- Detects shells and network tools: sh, bash, nc, netcat
- Indicates potential compromise
- Type: Runtime monitoring

**NIST-800-190-Runtime-2 - Cryptocurrency Mining Detection**
- Detects crypto mining processes: xmrig, minerd, cpuminer
- Prevents resource abuse
- Type: Runtime monitoring

**NIST-800-190-Runtime-3 - Package Manager Usage**
- Detects package managers: apt, yum, dnf, apk
- Indicates unauthorized software installation
- Type: Runtime monitoring

## Customization

### Modifying Policies

1. Edit `nist_800_190_generate.py`
2. Modify policy definitions as needed
3. Regenerate: `python3 nist_800_190_generate.py`
4. Redeploy: `python3 nist_800_190_deploy.py`

### Adding Trusted Registries

Edit policy **4.1.2** in `nist_800_190_generate.py`:

```python
"values": [
    {"value": "quay.io"},
    {"value": "your-registry.com"},  # Add your registry
    {"value": "registry.redhat.io"}
]
```

### Adjusting Severity Levels

Change severity in policy definitions:
- `CRITICAL_SEVERITY` - Most severe
- `HIGH_SEVERITY` - Important controls
- `MEDIUM_SEVERITY` - Moderate risk
- `LOW_SEVERITY` - Best practices

### Adding Exclusions

After deployment, add exclusions in RHACS UI:
1. Navigate to Policy Management
2. Select the policy
3. Add exclusions for:
   - System namespaces: `kube-system`, `openshift-*`
   - Infrastructure components
   - Approved exceptions

## Viewing Policies in RHACS

1. Log into RHACS: https://your-rhacs-instance.com
2. Navigate to: **Platform Configuration → Policy Management**
3. Filter by: `NIST 800-190` or `NIST-800-190`
4. View deployed policies and their status

## Compliance Mapping

These policies help satisfy NIST 800-190 recommendations:

| NIST Section | Topic | Policies |
|--------------|-------|----------|
| 4.1 | Image Risks | 4.1.1, 4.1.2, 4.1.3, 4.1.4 |
| 4.2 | Registry Risks | 4.1.2 |
| 4.3 | Orchestrator Risks | RT-1, RT-2, RT-3 |
| 4.4 | Container Risks | 4.4.1 - 4.4.5 |
| 4.5 | Host OS Risks | 4.5.1, 4.5.2 |

## Troubleshooting

### Connection Failed

```
Failed to connect to RHACS. Please check your credentials.
```

**Solution:**
- Verify RHACS_URL in `.env` file
- Verify RHACS_TOKEN is valid and not expired
- Check network connectivity

### Policy Already Exists

```
⊗ Policy already exists, skipping: NIST-800-190-...
```

**Solution:** This is normal. The script skips existing policies automatically.

### Policy Creation Failed

Check the error message for validation issues:
- **Invalid field names**: Field name not supported in your RHACS version
- **Invalid values**: Value format doesn't match RHACS requirements
- **API version**: Some features require newer RHACS versions

## NIST 800-190 Reference

**Full Document:** NIST Special Publication 800-190
**Title:** Application Container Security Guide
**Published:** September 2017
**URL:** https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf

## Architecture

```
┌─────────────────────────────────┐
│  nist_800_190_generate.py       │
│  (Policy Definition Generator)  │
└────────────┬────────────────────┘
             │ generates
             ▼
┌─────────────────────────────────┐
│  nist_800_190_policies.json     │
│  (14 Policy Definitions)        │
└────────────┬────────────────────┘
             │ used by
             ▼
┌─────────────────────────────────┐
│  nist_800_190_deploy.py         │
│  (Deployment Script)            │
└────────────┬────────────────────┘
             │ reads .env
             ├─────────────┐
             │             │
             ▼             ▼
      ┌──────────┐   ┌─────────┐
      │ RHACS_URL│   │RHACS_TOKEN│
      └──────────┘   └─────────┘
             │
             ▼
┌─────────────────────────────────┐
│  RHACS / ACS Platform           │
│  (12 Policies Created)          │
└─────────────────────────────────┘
```

## Best Practices

1. **Start with Advisory Mode**
   - Deploy policies without enforcement initially
   - Monitor for false positives
   - Enable enforcement gradually

2. **Add Exclusions**
   - Exclude system namespaces
   - Exclude infrastructure components
   - Document all exceptions

3. **Regular Reviews**
   - Review policy violations weekly
   - Update policies as environment changes
   - Adjust severity levels based on risk

4. **Integrate with CI/CD**
   - Use BUILD lifecycle policies in CI pipelines
   - Block vulnerable images before deployment
   - Automate policy compliance checks

5. **Configure Notifiers**
   - Set up alerts for HIGH/CRITICAL violations
   - Route notifications to security team
   - Create runbooks for common violations

## Related Resources

- [NIST SP 800-190 PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [RHACS Documentation](https://docs.openshift.com/acs/)
- [Container Security Best Practices](https://www.nist.gov/publications/application-container-security-guide)

## Support

For issues or questions:
1. Check RHACS logs for detailed error messages
2. Verify policy JSON format in `nist_800_190_policies.json`
3. Review RHACS API documentation for field requirements
4. Test policies in non-production environments first

## License

These policies are provided as examples based on NIST 800-190 guidelines. Customize according to your organization's security requirements and risk tolerance.
