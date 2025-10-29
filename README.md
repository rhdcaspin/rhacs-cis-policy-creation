# RHACS CIS Policy Creator

This Python script connects to Red Hat Advanced Cluster Security (RHACS) and automatically creates security policies based on CIS (Center for Internet Security) benchmarks for both Kubernetes and Docker environments, plus Post-Quantum Cryptography (PQC) policies to prepare for quantum-resistant security.

The policies are defined in external JSON configuration files (`cis_policies.json`, `pqc_policy.json`), making them easy to customize, maintain, and extend without modifying the core scripts.

## Files Structure

### Core Scripts
- **`rhacs_cis_policy_creator.py`** - Main script with RHACS API client and CIS policy creation logic
- **`pqc_policy_creator.py`** - Dedicated script for Post-Quantum Cryptography policy creation
- **`data_sovereignty_policy_creator.py`** - Dedicated script for Data Sovereignty policy creation
- **`integrate_pqc_policies.py`** - Script to merge PQC policies with existing CIS policies
- **`cisa_kev_policy_creator.py`** - Daily agent for CISA Known Exploited Vulnerabilities policies
- **`deduplicate_policies.py`** - Script to find and remove duplicate policies

### Configuration Files
- **`config.json`** - Main configuration file (create from template, contains sensitive data)
- **`config.json.template`** - Template for main configuration file
- **`cis_policies.json`** - External configuration file containing all CIS policy definitions
- **`pqc_policy.json`** - Post-Quantum Cryptography policy definitions
- **`data_sovereignty_policies.json`** - Data Sovereignty and geographic data residency policy definitions

### Documentation & Dependencies
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore file to protect sensitive configuration
- **`README.md`** - This documentation file
- **`DATA_SOVEREIGNTY_GUIDE.md`** - Comprehensive guide for Data Sovereignty policies
- **`GITHUB_SETUP.md`** - Guide for setting up the project on GitHub

## Features

### CIS Benchmark Policies

- **Kubernetes CIS Policies**: Implements key CIS Kubernetes benchmark controls including:
  - Minimize privileged containers (5.1.1)
  - Minimize hostNetwork usage (5.1.2)
  - Minimize hostPID and hostIPC usage (5.1.3)
  - Minimize allowPrivilegeEscalation (5.1.4)
  - Minimize root containers (5.1.5)

- **Docker CIS Policies**: Implements key CIS Docker benchmark controls including:
  - Ensure image is not running as root (4.1)
  - Ensure sensitive host system directories are not mounted (4.7)
  - Ensure AppArmor profile is enabled (5.1)
  - Ensure privileged ports are not mapped (5.7)
  - Ensure container is restricted from acquiring additional privileges (5.25)

### Post-Quantum Cryptography (PQC) Policies

- **PQC-1**: Enforce Post-Quantum Cryptography Standards
  - Detects deprecated crypto libraries vulnerable to quantum attacks
  - Identifies weak environment variable configurations
  - Ensures migration away from vulnerable OpenSSL versions

- **PQC-2**: Detect Weak RSA Key Configurations
  - Identifies RSA keys smaller than 3072 bits
  - Detects vulnerable key size environment variables
  - Prepares for transition to quantum-resistant algorithms

- **PQC-3**: Detect Deprecated Hash Algorithms
  - Identifies MD5 and SHA-1 usage in containers
  - Detects weak hash configurations in environment variables
  - Promotes SHA-256, SHA-3, or post-quantum hash functions

- **PQC-4**: Require PQC-Ready Libraries
  - Ensures containers include quantum-resistant cryptographic libraries
  - Checks for OpenSSL 3.0+, liboqs, Bouncy Castle with PQC support
  - Promotes adoption of PQC-enabled frameworks

- **PQC-5**: Detect Legacy TLS Cipher Suites
  - Identifies TLS configurations vulnerable to quantum attacks
  - Detects ECDHE, RSA, and DHE cipher suites
  - Prepares for hybrid classical-quantum TLS implementations

### Data Sovereignty Policies

- **Data Sovereignty Controls**: Comprehensive policies to enforce geographic data residency and compliance
  - **Geographic Node Placement**: Ensure workloads are scheduled only on nodes in approved regions (EU, US, etc.)
  - **Cross-Region Data Transfer Prevention**: Detect and prevent unauthorized data transfer across boundaries
  - **Registry and Supply Chain Controls**: Restrict container images to approved regional registries
  - **Storage and Data Persistence**: Ensure data at rest remains within geographic boundaries
  - **Backup and Disaster Recovery**: Enforce regional backup storage requirements
  - **Service Mesh Controls**: Prevent traffic routing across geographic boundaries
  - **Runtime Detection**: Detect unauthorized cloud API access and database connections

**Regulatory Compliance Support**:
  - GDPR (EU General Data Protection Regulation)
  - CCPA (California Consumer Privacy Act)
  - LGPD (Brazil Lei Geral de Proteção de Dados)
  - PIPEDA (Canada Personal Information Protection)
  - APPI (Japan Act on Protection of Personal Information)

**15 Comprehensive Policies** covering:
  - Node placement enforcement (EU/US regions)
  - Container registry restrictions
  - Data classification requirements
  - Storage class controls
  - Cloud provider API monitoring
  - Database connection auditing
  - Backup service restrictions

See **`DATA_SOVEREIGNTY_GUIDE.md`** for detailed implementation guidance.

### Threat Intelligence Integration

- **CISA KEV Policies**: Automatically creates policies for Known Exploited Vulnerabilities
  - Daily synchronization with CISA KEV catalog
  - Filters for container-relevant vulnerabilities
  - Creates deploy-time CVE blocking policies

## Prerequisites

- Python 3.7 or higher
- Access to RHACS Central instance
- Valid RHACS API token with policy creation permissions

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the script, you need to create a configuration file:

1. Copy the template configuration file:
   ```bash
   cp config.json.template config.json
   ```

2. Edit `config.json` with your RHACS details:
   ```json
   {
     "rhacs": {
       "central_url": "https://your-rhacs-central.example.com:443",
       "api_token": "your-rhacs-api-token-here"
     },
     "logging": {
       "level": "INFO",
       "format": "%(asctime)s - %(levelname)s - %(message)s"
     },
     "policies": {
       "config_file": "cis_policies.json",
       "skip_existing": true
     }
   }
   ```

### Configuration Options:

- **`rhacs.central_url`**: Your RHACS Central URL
- **`rhacs.api_token`**: Your RHACS API token with policy creation permissions
- **`logging.level`**: Log level (DEBUG, INFO, WARNING, ERROR)
- **`logging.format`**: Log message format
- **`policies.config_file`**: Path to CIS policies configuration file
- **`policies.skip_existing`**: Whether to skip policies that already exist (true/false)

**Security Note**: The `config.json` file contains sensitive credentials and is excluded from version control.

## Usage

### CIS Benchmark Policies

Run the main CIS policy script:

```bash
python3 rhacs_cis_policy_creator.py
```

The script will:

1. Connect to your RHACS Central instance
2. Check for existing policies to avoid duplicates
3. Create new CIS benchmark-based policies
4. Provide a summary of actions taken

### Post-Quantum Cryptography (PQC) Policies

#### Option 1: Create PQC Policies Separately
```bash
python3 pqc_policy_creator.py
```

#### Option 2: Integrate PQC with CIS Policies
```bash
python3 integrate_pqc_policies.py
python3 rhacs_cis_policy_creator.py
```

This approach adds PQC policies to your `cis_policies.json` file and creates them alongside CIS policies.

### Data Sovereignty Policies

Run the Data Sovereignty policy creator:

```bash
# Create all data sovereignty policies
python3 data_sovereignty_policy_creator.py

# Or include them with CIS policies (after integration)
python3 rhacs_cis_policy_creator.py
```

**Important**: Before deploying data sovereignty policies:
1. Review and customize region-specific values in `data_sovereignty_policies.json`
2. Ensure cluster nodes are properly labeled with geographic information
3. Label namespaces and workloads with data classification tags
4. Test policies in non-production environments first
5. See `DATA_SOVEREIGNTY_GUIDE.md` for complete configuration instructions

### CISA KEV Policies (Daily Agent)

Run the CISA Known Exploited Vulnerabilities agent:

```bash
# One-time execution
python3 cisa_kev_policy_creator.py

# Daily agent (runs continuously)
python3 -c "
from cisa_kev_policy_creator import main
if __name__ == '__main__':
    main()
"
```

### Policy Management

#### Find and Remove Duplicates
```bash
python3 deduplicate_policies.py
```

#### View All Available Scripts
```bash
ls -la *.py
```

## Policy Details

### Kubernetes CIS Policies

All Kubernetes policies are configured with:
- **Severity**: HIGH_SEVERITY
- **Lifecycle Stage**: DEPLOY
- **Enforcement**: FAIL_DEPLOYMENT
- **Category**: Security Best Practices

### Docker CIS Policies

Docker policies vary in severity and enforcement based on the specific control:
- Build-time checks use FAIL_BUILD_ENFORCEMENT
- Runtime checks use FAIL_DEPLOYMENT
- Severity ranges from MEDIUM to HIGH based on risk level

### Post-Quantum Cryptography (PQC) Policies

PQC policies are designed to detect quantum-vulnerable cryptographic implementations:

- **Lifecycle Stage**: DEPLOY (prevents vulnerable containers from being deployed)
- **Enforcement Actions**: 
  - FAIL_DEPLOYMENT for critical crypto vulnerabilities (PQC-1, PQC-2, PQC-5)
  - No enforcement for advisory policies (PQC-4)
- **Severity Levels**:
  - HIGH_SEVERITY: Deprecated crypto libraries, weak RSA configurations
  - MEDIUM_SEVERITY: Weak hash algorithms, legacy TLS cipher suites
  - LOW_SEVERITY: Missing PQC-ready libraries (advisory only)

#### Detection Methods:

1. **Image Component Analysis**: Scans for vulnerable cryptographic libraries
2. **Environment Variable Inspection**: Detects crypto-related configuration
3. **Container Configuration Review**: Identifies weak cryptographic settings

#### Quantum Threat Preparation:

These policies help organizations prepare for the post-quantum era by:
- Identifying current quantum-vulnerable implementations
- Promoting adoption of quantum-resistant algorithms
- Ensuring compliance with NIST post-quantum cryptography standards
- Supporting gradual migration to PQC-ready libraries

## Logging

The script provides detailed logging including:
- Connection status
- Policy creation results
- Error messages for troubleshooting
- Final summary of actions taken

## Error Handling

The script includes comprehensive error handling for:
- Network connectivity issues
- Authentication failures
- API errors
- Duplicate policy detection

## Security Considerations

- **Configuration File Security**: The `config.json` file contains sensitive API tokens and is excluded from version control via `.gitignore`
- **SSL Verification**: The script disables SSL verification for demo environments only
- **API Token Storage**: 
  - Store API tokens securely in production environments
  - Consider using environment variables or secure vaults for sensitive credentials
  - Rotate API tokens regularly according to your security policy
- **Access Control**: Ensure the API token has only the minimum required permissions for policy creation
- **File Permissions**: Set appropriate file permissions on configuration files (e.g., `chmod 600 config.json`)

## Policy Configuration

The CIS policies are defined in the `cis_policies.json` file with the following structure:

```json
{
  "kubernetes_policies": [
    {
      "name": "Policy Name",
      "description": "Policy description",
      "rationale": "Why this policy exists",
      "remediation": "How to fix violations",
      "severity": "HIGH_SEVERITY|MEDIUM_SEVERITY|LOW_SEVERITY",
      "enforcementActions": ["FAIL_DEPLOYMENT", "FAIL_BUILD_ENFORCEMENT"],
      "policySections": [...],
      "mitreAttackVectors": [...]
    }
  ],
  "docker_policies": [...]
}
```

### Key Configuration Fields:

- **name**: Unique policy identifier
- **severity**: Risk level (HIGH_SEVERITY, MEDIUM_SEVERITY, LOW_SEVERITY)
- **lifecycleStages**: When policy applies (BUILD, DEPLOY, RUNTIME)
- **enforcementActions**: What happens on violation (FAIL_DEPLOYMENT, FAIL_BUILD_ENFORCEMENT)
- **policySections**: RHACS policy logic and conditions
- **mitreAttackVectors**: MITRE ATT&CK framework mappings

## Customization

To add additional CIS policies:

1. Edit the `cis_policies.json` file
2. Add new policy objects to the `kubernetes_policies` or `docker_policies` arrays
3. Follow the existing policy structure and RHACS API format
4. Test the new policies in a development environment first

### Custom Configuration File

You can use a different configuration file by modifying the script:

```python
generator = CISPolicyGenerator("my_custom_policies.json")
```

## Troubleshooting

- **Configuration Issues**: 
  - Ensure `config.json` exists and is valid JSON
  - Verify all required fields are present in the configuration
  - Check file permissions on configuration files
- **Connection Issues**: 
  - Verify your RHACS central_url in `config.json`
  - Check network connectivity to RHACS Central
  - Ensure the URL includes the correct port (usually :443)
- **Authentication Failures**: 
  - Check your API token validity and permissions in `config.json`
  - Verify the token has policy creation permissions
  - Ensure the token hasn't expired
- **Policy Creation Failures**: 
  - Review the logs for specific error messages
  - Check RHACS API documentation for field requirements
- **Duplicate Policies**: 
  - The script skips existing policies when `skip_existing` is true
  - Set `skip_existing` to false to attempt updates to existing policies

## Quick Start Guide

### 1. Deploy All Security Policies

```bash
# Install dependencies
pip install -r requirements.txt

# Configure RHACS connection
cp config.json.template config.json
# Edit config.json with your RHACS URL and API token

# Deploy CIS Benchmark policies
python3 rhacs_cis_policy_creator.py

# Deploy Post-Quantum Cryptography policies
python3 pqc_policy_creator.py

# Deploy Data Sovereignty policies (customize first!)
# Edit data_sovereignty_policies.json for your regions
python3 data_sovereignty_policy_creator.py

# Set up CISA KEV monitoring (optional)
python3 cisa_kev_policy_creator.py
```

### 2. For Data Sovereignty Only

If you only need data sovereignty enforcement:

```bash
# Configure RHACS
cp config.json.template config.json

# Customize policies for your regions
# Edit data_sovereignty_policies.json

# Label your cluster nodes with geographic info
kubectl label nodes <node-name> topology.kubernetes.io/region=eu-west-1

# Deploy policies
python3 data_sovereignty_policy_creator.py

# Verify in RHACS UI
# Navigate to Platform Configuration → Policy Management
# Filter by "Data-Sovereignty"
```

See `DATA_SOVEREIGNTY_GUIDE.md` for comprehensive setup instructions.

## Additional Resources

- **Data Sovereignty**: See `DATA_SOVEREIGNTY_GUIDE.md` for complete implementation guide
- **GitHub Setup**: See `GITHUB_SETUP.md` for repository configuration
- **Policy Customization**: Edit JSON policy files to match your requirements

## Support

For issues related to:
- RHACS API: Consult the [RHACS documentation](https://docs.openshift.com/acs/)
- CIS Benchmarks: Refer to the [official CIS Kubernetes and Docker benchmarks](https://www.cisecurity.org/cis-benchmarks)
- Data Sovereignty: See `DATA_SOVEREIGNTY_GUIDE.md` for troubleshooting
- Script Issues: Check the logs and error messages for troubleshooting guidance 