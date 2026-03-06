#!/usr/bin/env python3
"""
NIST 800-190 Policy Generator

This script generates RHACS security policies based on NIST SP 800-190 
Application Container Security Guide recommendations.

NIST 800-190 covers five major areas:
1. Image Security
2. Registry Security  
3. Orchestrator Security
4. Container Runtime Security
5. Host OS Security

This script creates the policy JSON definitions only.
Use nist_800_190_deploy.py to deploy them to RHACS.
"""

import json
import sys


def generate_nist_800_190_policies():
    """Generate NIST 800-190 compliant RHACS policies."""
    
    policies = {
        "nist_800_190_policies": [
            # Image Security Policies
            {
                "name": "NIST-800-190-4.1.1 - Image Vulnerabilities Not Scanned",
                "description": "NIST 800-190 Section 4.1: Ensure all images are scanned for vulnerabilities before deployment",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Vulnerability Management"
                ],
                "lifecycleStages": [
                    "BUILD",
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_BUILD_ENFORCEMENT",
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Image Assurance",
                        "policyGroups": [
                            {
                                "fieldName": "Image Age",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "90"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0001",
                        "techniques": [
                            "T1190"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.1.2 - Insecure Container Images",
                "description": "NIST 800-190 Section 4.1: Do not use images from untrusted registries",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Supply Chain Security"
                ],
                "lifecycleStages": [
                    "BUILD",
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_BUILD_ENFORCEMENT",
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Image Registry",
                        "policyGroups": [
                            {
                                "fieldName": "Image Registry",
                                "booleanOperator": "OR",
                                "negate": True,
                                "values": [
                                    {
                                        "value": "quay.io"
                                    },
                                    {
                                        "value": "registry.redhat.io"
                                    },
                                    {
                                        "value": "gcr.io"
                                    },
                                    {
                                        "value": ".*\\.dkr\\.ecr\\..*\\.amazonaws\\.com"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0001",
                        "techniques": [
                            "T1195"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.1.3 - Images Without Signature Verification",
                "description": "NIST 800-190 Section 4.1: Ensure image integrity through signature verification",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Supply Chain Security"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "MEDIUM_SEVERITY",
                "enforcementActions": [],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Image Signature",
                        "policyGroups": [
                            {
                                "fieldName": "Image Signature Verified By",
                                "booleanOperator": "OR",
                                "negate": True,
                                "values": [
                                    {
                                        "value": ".*"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0001",
                        "techniques": [
                            "T1195"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.1.4 - Root User in Container",
                "description": "NIST 800-190 Section 4.1: Containers should not run as root user",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Privilege Escalation"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Container Configuration",
                        "policyGroups": [
                            {
                                "fieldName": "Image User",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "root"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1548"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            # Container Runtime Security Policies
            {
                "name": "NIST-800-190-4.4.1 - Privileged Containers",
                "description": "NIST 800-190 Section 4.4: Restrict privileged containers that have root capabilities",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Container Runtime"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "CRITICAL_SEVERITY",
                "enforcementActions": [
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Container Configuration",
                        "policyGroups": [
                            {
                                "fieldName": "Privileged Container",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "true"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1611"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.4.2 - Host Namespace Sharing",
                "description": "NIST 800-190 Section 4.4: Do not share host network, PID, or IPC namespaces",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Container Runtime"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Namespace Isolation",
                        "policyGroups": [
                            {
                                "fieldName": "Host Network",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "true"
                                    }
                                ]
                            },
                            {
                                "fieldName": "Host PID",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "true"
                                    }
                                ]
                            },
                            {
                                "fieldName": "Host IPC",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "true"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1611"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.4.3 - Resource Limits Not Set",
                "description": "NIST 800-190 Section 4.4: Set resource limits to prevent resource exhaustion attacks",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Resource Management"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "MEDIUM_SEVERITY",
                "enforcementActions": [],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Resource Configuration",
                        "policyGroups": [
                            {
                                "fieldName": "Memory Limit (MB)",
                                "booleanOperator": "OR",
                                "negate": True,
                                "values": [
                                    {
                                        "value": ".*"
                                    }
                                ]
                            },
                            {
                                "fieldName": "CPU Cores Limit",
                                "booleanOperator": "OR",
                                "negate": True,
                                "values": [
                                    {
                                        "value": ".*"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0040",
                        "techniques": [
                            "T1496"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.4.4 - Dangerous Linux Capabilities",
                "description": "NIST 800-190 Section 4.4: Restrict dangerous Linux capabilities",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Container Runtime"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Capabilities",
                        "policyGroups": [
                            {
                                "fieldName": "Add Capabilities",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "SYS_ADMIN"
                                    },
                                    {
                                        "value": "NET_ADMIN"
                                    },
                                    {
                                        "value": "SYS_MODULE"
                                    },
                                    {
                                        "value": "SYS_PTRACE"
                                    },
                                    {
                                        "value": "SYS_BOOT"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1548"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.4.5 - Privilege Escalation Allowed",
                "description": "NIST 800-190 Section 4.4: Prevent privilege escalation in containers",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Privilege Escalation"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Security Context",
                        "policyGroups": [
                            {
                                "fieldName": "Allow Privilege Escalation",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "true"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1548"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            # Host OS Security Policies
            {
                "name": "NIST-800-190-4.5.1 - Sensitive Host Paths Mounted",
                "description": "NIST 800-190 Section 4.5: Do not mount sensitive host directories",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Host Security"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [
                    "FAIL_DEPLOYMENT"
                ],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Volume Mounts",
                        "policyGroups": [
                            {
                                "fieldName": "Volume Source",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "/"
                                    },
                                    {
                                        "value": "/boot"
                                    },
                                    {
                                        "value": "/dev"
                                    },
                                    {
                                        "value": "/etc"
                                    },
                                    {
                                        "value": "/lib"
                                    },
                                    {
                                        "value": "/proc"
                                    },
                                    {
                                        "value": "/sys"
                                    },
                                    {
                                        "value": "/usr"
                                    },
                                    {
                                        "value": "/var/run/docker.sock"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1611"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-4.5.2 - HostPath Volumes Used",
                "description": "NIST 800-190 Section 4.5: Minimize use of HostPath volumes",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Host Security"
                ],
                "lifecycleStages": [
                    "DEPLOY"
                ],
                "eventSource": "NOT_APPLICABLE",
                "exclusions": [],
                "scope": [],
                "severity": "MEDIUM_SEVERITY",
                "enforcementActions": [],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Volume Types",
                        "policyGroups": [
                            {
                                "fieldName": "Volume Type",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "HostPath"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0004",
                        "techniques": [
                            "T1611"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            # Runtime Security Policies
            {
                "name": "NIST-800-190-Runtime-1 - Unauthorized Process Execution",
                "description": "NIST 800-190 Runtime: Detect unauthorized process execution in containers",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Runtime Security"
                ],
                "lifecycleStages": [
                    "RUNTIME"
                ],
                "eventSource": "DEPLOYMENT_EVENT",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Process Execution",
                        "policyGroups": [
                            {
                                "fieldName": "Process Name",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "/bin/sh"
                                    },
                                    {
                                        "value": "/bin/bash"
                                    },
                                    {
                                        "value": "nc"
                                    },
                                    {
                                        "value": "netcat"
                                    },
                                    {
                                        "value": "ncat"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0002",
                        "techniques": [
                            "T1059"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-Runtime-2 - Cryptocurrency Mining Detection",
                "description": "NIST 800-190 Runtime: Detect cryptocurrency mining processes",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Runtime Security"
                ],
                "lifecycleStages": [
                    "RUNTIME"
                ],
                "eventSource": "DEPLOYMENT_EVENT",
                "exclusions": [],
                "scope": [],
                "severity": "HIGH_SEVERITY",
                "enforcementActions": [],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Crypto Mining",
                        "policyGroups": [
                            {
                                "fieldName": "Process Name",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "xmrig"
                                    },
                                    {
                                        "value": "minerd"
                                    },
                                    {
                                        "value": "cpuminer"
                                    },
                                    {
                                        "value": "cryptonight"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0040",
                        "techniques": [
                            "T1496"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            },
            {
                "name": "NIST-800-190-Runtime-3 - Package Manager Usage",
                "description": "NIST 800-190 Runtime: Detect package manager usage indicating unauthorized software installation",
                "disabled": False,
                "categories": [
                    "NIST 800-190",
                    "Runtime Security"
                ],
                "lifecycleStages": [
                    "RUNTIME"
                ],
                "eventSource": "DEPLOYMENT_EVENT",
                "exclusions": [],
                "scope": [],
                "severity": "MEDIUM_SEVERITY",
                "enforcementActions": [],
                "notifiers": [],
                "policyVersion": "1.1",
                "policySections": [
                    {
                        "sectionName": "Package Management",
                        "policyGroups": [
                            {
                                "fieldName": "Process Name",
                                "booleanOperator": "OR",
                                "negate": False,
                                "values": [
                                    {
                                        "value": "apt"
                                    },
                                    {
                                        "value": "apt-get"
                                    },
                                    {
                                        "value": "yum"
                                    },
                                    {
                                        "value": "dnf"
                                    },
                                    {
                                        "value": "apk"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "mitreAttackVectors": [
                    {
                        "tactic": "TA0003",
                        "techniques": [
                            "T1505"
                        ]
                    }
                ],
                "criteriaLocked": False,
                "mitreVectorsLocked": False,
                "isDefault": False
            }
        ]
    }
    
    return policies


def main():
    """Main function to generate NIST 800-190 policies."""
    print("=" * 80)
    print("NIST SP 800-190 Policy Generator")
    print("Application Container Security Guide")
    print("=" * 80)
    print()
    
    # Generate policies
    policies = generate_nist_800_190_policies()
    
    # Save to JSON file
    output_file = "nist_800_190_policies.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(policies, f, indent=2)
        
        policy_count = len(policies['nist_800_190_policies'])
        print(f"✓ Successfully generated {policy_count} NIST 800-190 policies")
        print(f"✓ Saved to: {output_file}")
        print()
        
        # Summary
        print("Policy Summary:")
        print("-" * 80)
        
        by_category = {}
        by_severity = {}
        by_lifecycle = {}
        
        for policy in policies['nist_800_190_policies']:
            # Count by category
            for cat in policy['categories']:
                by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by severity
            severity = policy['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by lifecycle
            for stage in policy['lifecycleStages']:
                by_lifecycle[stage] = by_lifecycle.get(stage, 0) + 1
        
        print("\nBy Severity:")
        for severity, count in sorted(by_severity.items(), reverse=True):
            print(f"  {severity}: {count}")
        
        print("\nBy Lifecycle Stage:")
        for stage, count in sorted(by_lifecycle.items()):
            print(f"  {stage}: {count}")
        
        print("\nBy Category:")
        for category, count in sorted(by_category.items()):
            print(f"  {category}: {count}")
        
        print()
        print("=" * 80)
        print("Next Steps:")
        print("  1. Review the generated policies in nist_800_190_policies.json")
        print("  2. Customize policies as needed for your environment")
        print("  3. Deploy to RHACS using: python3 nist_800_190_deploy.py")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"✗ Error generating policies: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
