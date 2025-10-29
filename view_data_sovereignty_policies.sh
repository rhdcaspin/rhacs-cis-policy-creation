#!/bin/bash
# Data Sovereignty Policy Viewer
# Quick script to view all data sovereignty policies

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║               DATA SOVEREIGNTY POLICIES - DETAILED VIEW                      ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Install with:"
    echo "  macOS: brew install jq"
    echo "  Linux: apt-get install jq  or  yum install jq"
    exit 1
fi

if [ ! -f "data_sovereignty_policies.json" ]; then
    echo "Error: data_sovereignty_policies.json not found in current directory"
    exit 1
fi

POLICIES=$(jq -r '.data_sovereignty_policies | length' data_sovereignty_policies.json)
echo "Total Policies: $POLICIES"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for i in $(seq 0 $((POLICIES-1))); do
    NAME=$(jq -r ".data_sovereignty_policies[$i].name" data_sovereignty_policies.json)
    DESC=$(jq -r ".data_sovereignty_policies[$i].description" data_sovereignty_policies.json)
    SEVERITY=$(jq -r ".data_sovereignty_policies[$i].severity" data_sovereignty_policies.json)
    LIFECYCLE=$(jq -r ".data_sovereignty_policies[$i].lifecycleStages | join(\", \")" data_sovereignty_policies.json)
    ENFORCEMENT=$(jq -r ".data_sovereignty_policies[$i].enforcementActions | length" data_sovereignty_policies.json)
    CATEGORIES=$(jq -r ".data_sovereignty_policies[$i].categories | join(\", \")" data_sovereignty_policies.json)
    
    # Color code severity
    case $SEVERITY in
        "CRITICAL_SEVERITY")
            SEV_COLOR="🔴 CRITICAL"
            ;;
        "HIGH_SEVERITY")
            SEV_COLOR="🟠 HIGH"
            ;;
        "MEDIUM_SEVERITY")
            SEV_COLOR="🟡 MEDIUM"
            ;;
        *)
            SEV_COLOR="⚪ $SEVERITY"
            ;;
    esac
    
    # Enforcement indicator
    if [ "$ENFORCEMENT" -gt 0 ]; then
        ENF_INDICATOR="✓ Enforced"
    else
        ENF_INDICATOR="○ Advisory"
    fi
    
    echo ""
    echo "Policy $((i+1)): $NAME"
    echo "  Severity:    $SEV_COLOR"
    echo "  Lifecycle:   $LIFECYCLE"
    echo "  Enforcement: $ENF_INDICATOR"
    echo "  Categories:  $CATEGORIES"
    echo "  Description: $DESC"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
done

echo ""
echo "Summary by Severity:"
echo "  🔴 CRITICAL: $(jq '[.data_sovereignty_policies[] | select(.severity=="CRITICAL_SEVERITY")] | length' data_sovereignty_policies.json)"
echo "  🟠 HIGH:     $(jq '[.data_sovereignty_policies[] | select(.severity=="HIGH_SEVERITY")] | length' data_sovereignty_policies.json)"
echo "  🟡 MEDIUM:   $(jq '[.data_sovereignty_policies[] | select(.severity=="MEDIUM_SEVERITY")] | length' data_sovereignty_policies.json)"
echo ""

echo "Summary by Enforcement:"
ENFORCED=$(jq '[.data_sovereignty_policies[] | select(.enforcementActions | length > 0)] | length' data_sovereignty_policies.json)
ADVISORY=$(jq '[.data_sovereignty_policies[] | select(.enforcementActions | length == 0)] | length' data_sovereignty_policies.json)
echo "  ✓ Enforced (blocks): $ENFORCED"
echo "  ○ Advisory (alerts): $ADVISORY"
echo ""

echo "Summary by Lifecycle:"
echo "  DEPLOY:  $(jq '[.data_sovereignty_policies[] | select(.lifecycleStages[] == "DEPLOY")] | length' data_sovereignty_policies.json)"
echo "  RUNTIME: $(jq '[.data_sovereignty_policies[] | select(.lifecycleStages[] == "RUNTIME")] | length' data_sovereignty_policies.json)"
echo "  BUILD:   $(jq '[.data_sovereignty_policies[] | select(.lifecycleStages[] == "BUILD")] | length' data_sovereignty_policies.json)"
echo ""

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                         DEPLOYMENT OPTIONS                                   ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Deploy all policies:"
echo "  python3 data_sovereignty_policy_creator.py"
echo ""
echo "View specific policy details:"
echo "  jq '.data_sovereignty_policies[0]' data_sovereignty_policies.json"
echo ""
echo "List all policy names:"
echo "  jq -r '.data_sovereignty_policies[].name' data_sovereignty_policies.json"
echo ""

