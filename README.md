# RHACS CIS Policy Creator

This Python script connects to Red Hat Advanced Cluster Security (RHACS) and automatically creates security policies based on CIS (Center for Internet Security) benchmarks for both Kubernetes and Docker environments.

The policies are defined in an external JSON configuration file (`cis_policies.json`), making them easy to customize, maintain, and extend without modifying the core script.

## Files Structure

- **`rhacs_cis_policy_creator.py`** - Main script with RHACS API client and policy creation logic
- **`config.json`** - Main configuration file (create from template, contains sensitive data)
- **`config.json.template`** - Template for main configuration file
- **`cis_policies.json`** - External configuration file containing all CIS policy definitions
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore file to protect sensitive configuration
- **`README.md`** - This documentation file

## Features

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

Run the script:

```bash
python3 rhacs_cis_policy_creator.py
```

The script will:

1. Connect to your RHACS Central instance
2. Check for existing policies to avoid duplicates
3. Create new CIS benchmark-based policies
4. Provide a summary of actions taken

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

## Support

For issues related to:
- RHACS API: Consult the RHACS documentation
- CIS Benchmarks: Refer to the official CIS Kubernetes and Docker benchmarks
- Script Issues: Check the logs and error messages for troubleshooting guidance 