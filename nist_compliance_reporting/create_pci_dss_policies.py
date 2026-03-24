#!/usr/bin/env python3
"""
PCI-DSS 4.0 Policy Creation for RHACS

This script creates PCI-DSS 4.0 compliance policies in Red Hat Advanced Cluster Security.
PCI-DSS (Payment Card Industry Data Security Standard) is an information security standard
for organizations that handle credit cards.

PCI-DSS 4.0 has 12 main requirements focused on protecting cardholder data.
"""

import requests
import json
import os
import sys
import urllib3

# Disable SSL warnings for demo environment
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# RHACS Configuration from environment variables
RHACS_URL = os.getenv('RHACS_URL', '').rstrip('/')
API_TOKEN = os.getenv('RHACS_API_TOKEN')
VERIFY_SSL = os.getenv('RHACS_VERIFY_SSL', 'false').lower() == 'true'

# Validate required environment variables
if not RHACS_URL:
    print("ERROR: RHACS_URL environment variable not set")
    print("Please set: export RHACS_URL='https://your-rhacs-instance.com'")
    sys.exit(1)

if not API_TOKEN:
    print("ERROR: RHACS_API_TOKEN environment variable not set")
    print("Please set: export RHACS_API_TOKEN='your-api-token'")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# PCI-DSS 4.0 Policy Definitions
PCI_DSS_POLICIES = [
    {
        "name": "PCI-DSS-Req-1.1-Network-Segmentation",
        "description": "PCI-DSS 4.0 Requirement 1: Install and maintain network security controls. Containers must not use host network mode to ensure proper network segmentation.",
        "rationale": "Using host network mode bypasses network isolation and violates PCI-DSS requirement for network segmentation to protect cardholder data environment (CDE).",
        "remediation": "Set hostNetwork to false in pod specifications to ensure containers use isolated network namespaces.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Host Network",
                        "values": [{"value": "true"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-1.2-Privileged-Container-Ports",
        "description": "PCI-DSS 4.0 Requirement 1: Restrict inbound and outbound traffic. Containers must not expose privileged ports (< 1024) that could be used to access the CDE.",
        "rationale": "Privileged ports may indicate services that should not be directly accessible, violating network security controls required by PCI-DSS.",
        "remediation": "Configure containers to use non-privileged ports (>= 1024) for services.",
        "categories": ["PCI"],
        "severity": "MEDIUM_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Exposed Port",
                        "values": [{"value": "< 1024"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-2.1-Secure-Configuration-Standards",
        "description": "PCI-DSS 4.0 Requirement 2: Apply secure configurations to all system components. Containers must not run as root user.",
        "rationale": "Running containers as root violates the principle of least privilege required by PCI-DSS for system hardening.",
        "remediation": "Set runAsUser to a non-zero value in securityContext or use a non-root base image.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "User",
                        "values": [{"value": "0"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-2.2-Privileged-Containers-Prohibited",
        "description": "PCI-DSS 4.0 Requirement 2: Develop configuration standards. Privileged containers are prohibited as they bypass security controls.",
        "rationale": "Privileged containers have access to all host resources and can compromise the entire CDE, violating PCI-DSS security configuration requirements.",
        "remediation": "Set privileged to false in container securityContext.",
        "categories": ["PCI"],
        "severity": "CRITICAL_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Privileged Container",
                        "values": [{"value": "true"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-2.3-Limit-Root-Filesystem-Write",
        "description": "PCI-DSS 4.0 Requirement 2: Configure systems securely. Containers should use read-only root filesystems to prevent tampering.",
        "rationale": "Read-only filesystems prevent malware and unauthorized modifications that could compromise cardholder data.",
        "remediation": "Set readOnlyRootFilesystem to true in container securityContext.",
        "categories": ["PCI"],
        "severity": "MEDIUM_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Read-Only Root Filesystem",
                        "values": [{"value": "false"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-3.1-Sensitive-Data-Protection",
        "description": "PCI-DSS 4.0 Requirement 3: Protect stored account data. Containers must not store sensitive authentication data (SAD) or cardholder data (CHD) in environment variables.",
        "rationale": "Environment variables are easily accessible and logged, violating PCI-DSS requirements for protecting sensitive data.",
        "remediation": "Use Kubernetes Secrets with proper encryption at rest, not environment variables, for sensitive data.",
        "categories": ["PCI"],
        "severity": "CRITICAL_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Environment Variable",
                        "values": [
                            {"value": ".*[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*"},
                            {"value": ".*[Cc][Rr][Ee][Dd][Ee][Nn][Tt][Ii][Aa][Ll].*"},
                            {"value": ".*[Cc][Aa][Rr][Dd].*"},
                            {"value": ".*[Tt][Oo][Kk][Ee][Nn].*"}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-4.1-Encryption-in-Transit",
        "description": "PCI-DSS 4.0 Requirement 4: Protect cardholder data with strong cryptography during transmission. Containers must use TLS/SSL for data transmission.",
        "rationale": "Unencrypted transmission of cardholder data violates PCI-DSS encryption requirements.",
        "remediation": "Configure applications to use TLS 1.2 or higher for all network communications involving cardholder data.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Exposed Port",
                        "values": [
                            {"value": "80"},
                            {"value": "8080"}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-5.1-Malware-Protection",
        "description": "PCI-DSS 4.0 Requirement 5: Protect all systems and networks from malicious software. Images must be scanned for vulnerabilities and malware.",
        "rationale": "Unscanned images may contain malware or vulnerabilities that could compromise the CDE.",
        "remediation": "Enable image scanning in RHACS and ensure all images are scanned before deployment.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Image Scan Status",
                        "values": [{"value": "NOT_SCANNED"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-6.1-Secure-Development",
        "description": "PCI-DSS 4.0 Requirement 6: Develop and maintain secure systems and software. Images must not have critical or high CVEs.",
        "rationale": "Known vulnerabilities in container images can be exploited to access cardholder data, violating PCI-DSS secure development requirements.",
        "remediation": "Update base images and dependencies to versions without critical or high severity CVEs.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "CVE",
                        "values": [
                            {"value": "CRITICAL"},
                            {"value": "IMPORTANT"}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-7.1-Least-Privilege-Access",
        "description": "PCI-DSS 4.0 Requirement 7: Restrict access by business need to know. Containers must not add dangerous capabilities.",
        "rationale": "Dangerous capabilities like NET_ADMIN, SYS_ADMIN provide excessive privileges violating the principle of least privilege.",
        "remediation": "Remove dangerous capabilities from container securityContext. Only add required capabilities.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Container Capability",
                        "values": [
                            {"value": "SYS_ADMIN"},
                            {"value": "NET_ADMIN"},
                            {"value": "SYS_MODULE"},
                            {"value": "SYS_RAWIO"}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-8.1-User-Identification",
        "description": "PCI-DSS 4.0 Requirement 8: Identify users and authenticate access. Service accounts must be properly configured and not use default tokens.",
        "rationale": "Automatic mounting of service account tokens without need violates authentication requirements.",
        "remediation": "Set automountServiceAccountToken to false unless explicitly required for the application.",
        "categories": ["PCI"],
        "severity": "MEDIUM_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Automount Service Account Token",
                        "values": [{"value": "true"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-9.1-Physical-Access-Host-Path",
        "description": "PCI-DSS 4.0 Requirement 9: Restrict physical access to cardholder data. Containers must not mount sensitive host paths.",
        "rationale": "Mounting host paths can expose sensitive files and bypass physical security controls required by PCI-DSS.",
        "remediation": "Avoid mounting host paths. Use Kubernetes volumes instead of hostPath volumes.",
        "categories": ["PCI"],
        "severity": "HIGH_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Volume Type",
                        "values": [{"value": "hostPath"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-10.1-Audit-Logging",
        "description": "PCI-DSS 4.0 Requirement 10: Log and monitor all access to system components and cardholder data. Containers must have proper logging configured.",
        "rationale": "Insufficient logging prevents detection of security events and violates PCI-DSS audit requirements.",
        "remediation": "Ensure containers output logs to stdout/stderr and configure centralized log collection.",
        "categories": ["PCI"],
        "severity": "MEDIUM_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Container CPU Request",
                        "values": [{"value": ".*"}]
                    }
                ]
            }
        ],
        "disabled": True,  # This is a placeholder - proper audit logging requires external configuration
        "description": "Note: This policy is disabled by default as audit logging should be configured at the cluster/namespace level."
    },
    {
        "name": "PCI-DSS-Req-11.1-Namespace-Isolation",
        "description": "PCI-DSS 4.0 Requirement 11: Test security of systems and networks regularly. Workloads processing cardholder data must use dedicated namespaces with network policies.",
        "rationale": "Proper namespace isolation is required to segment and protect the cardholder data environment during security testing.",
        "remediation": "Deploy CDE workloads to dedicated namespaces and implement NetworkPolicies to restrict traffic.",
        "categories": ["PCI"],
        "severity": "MEDIUM_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Namespace",
                        "values": [{"value": "default"}]
                    }
                ]
            }
        ]
    },
    {
        "name": "PCI-DSS-Req-12.1-Security-Policy-Labels",
        "description": "PCI-DSS 4.0 Requirement 12: Support information security with organizational policies. All CDE workloads must be properly labeled for identification.",
        "rationale": "Proper labeling ensures security policies can be applied and maintained according to PCI-DSS requirements.",
        "remediation": "Add labels such as 'pci-scope: cde' or 'data-classification: cardholder-data' to all CDE workloads.",
        "categories": ["PCI"],
        "severity": "LOW_SEVERITY",
        "policySection": [
            {
                "policyGroups": [
                    {
                        "fieldName": "Required Label",
                        "values": [{"value": "app"}]
                    }
                ]
            }
        ],
        "disabled": True  # Disabled by default - organizations should customize required labels
    }
]

def create_policy(policy_definition):
    """Create a single policy in RHACS"""

    # Build the full policy object
    policy = {
        "name": policy_definition["name"],
        "description": policy_definition["description"],
        "rationale": policy_definition["rationale"],
        "remediation": policy_definition["remediation"],
        "categories": policy_definition["categories"],
        "severity": policy_definition["severity"],
        "disabled": policy_definition.get("disabled", False),
        "lifecycleStages": ["DEPLOY"],
        "exclusions": [],
        "scope": [],
        "policyVersion": "1.1",
        "policySections": policy_definition["policySection"]
    }

    url = f"{RHACS_URL}/v1/policies"

    try:
        response = requests.post(url, headers=HEADERS, json=policy, verify=VERIFY_SSL)

        if response.status_code == 200:
            return True, "Created successfully"
        elif response.status_code == 409:
            return False, "Policy already exists"
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

def main():
    print("=" * 80)
    print("PCI-DSS 4.0 Policy Creation for RHACS")
    print("=" * 80)
    print()
    print(f"RHACS URL: {RHACS_URL}")
    print(f"Total policies to create: {len(PCI_DSS_POLICIES)}")
    print()

    created = 0
    skipped = 0
    failed = 0

    for policy_def in PCI_DSS_POLICIES:
        policy_name = policy_def["name"]
        print(f"Creating: {policy_name}")

        success, message = create_policy(policy_def)

        if success:
            print(f"  ✓ {message}")
            created += 1
        elif "already exists" in message:
            print(f"  ⊙ {message}")
            skipped += 1
        else:
            print(f"  ✗ {message}")
            failed += 1

        print()

    print("=" * 80)
    print("PCI-DSS 4.0 Policy Creation Summary")
    print("=" * 80)
    print(f"Created:  {created}")
    print(f"Skipped:  {skipped} (already exist)")
    print(f"Failed:   {failed}")
    print(f"Total:    {len(PCI_DSS_POLICIES)}")
    print()

    if created > 0 or skipped > 0:
        print("✓ PCI-DSS 4.0 policies are ready!")
        print()
        print("Next steps:")
        print("  1. Review policies in RHACS console")
        print("  2. Customize policies for your environment")
        print("  3. Generate compliance report:")
        print("     python3 universal_compliance_report.py --framework pci-dss")
        print("  4. Generate HTML dashboard:")
        print("     python3 universal_html_dashboard.py --framework pci-dss")
        print()

if __name__ == "__main__":
    main()
