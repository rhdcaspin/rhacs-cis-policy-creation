#!/bin/bash
#
# Generate Compliance Reports for All Frameworks
#
# This script generates compliance reports for all supported frameworks
# in the RHACS instance.
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Multi-Framework Compliance Report Generation                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check environment variables
if [ -z "$RHACS_URL" ]; then
    echo "ERROR: RHACS_URL environment variable not set"
    echo "Please run: export RHACS_URL='https://your-rhacs-instance.com'"
    exit 1
fi

if [ -z "$RHACS_API_TOKEN" ]; then
    echo "ERROR: RHACS_API_TOKEN environment variable not set"
    echo "Please run: export RHACS_API_TOKEN='your-api-token'"
    exit 1
fi

# Frameworks to generate reports for
FRAMEWORKS=(
    "nist-800-190"
    "nist-800-53"
    "pci-dss"
    "hipaa"
    "cis-kubernetes"
    "iso-27001"
    "soc2"
    "fedramp"
    "gdpr"
)

GENERATED_COUNT=0
FAILED_COUNT=0

# Create output directory
OUTPUT_DIR="compliance_reports_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "Output directory: $OUTPUT_DIR"
echo ""

# Generate reports for each framework
for framework in "${FRAMEWORKS[@]}"
do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Generating report for: $framework"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if python3 universal_compliance_report.py --framework "$framework" > "$OUTPUT_DIR/${framework}_console.log" 2>&1; then
        echo "✅ $framework: SUCCESS"

        # Move generated JSON to output directory
        mv ${framework}_compliance_report_*.json "$OUTPUT_DIR/" 2>/dev/null || true

        GENERATED_COUNT=$((GENERATED_COUNT + 1))
    else
        echo "❌ $framework: FAILED (check ${OUTPUT_DIR}/${framework}_console.log)"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
    echo ""
done

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Report Generation Complete                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  Generated: $GENERATED_COUNT reports"
echo "  Failed:    $FAILED_COUNT reports"
echo "  Output:    $OUTPUT_DIR/"
echo ""

# List generated files
if [ $GENERATED_COUNT -gt 0 ]; then
    echo "Generated Reports:"
    ls -lh "$OUTPUT_DIR"/*.json 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    echo ""
fi

# Create index file
INDEX_FILE="$OUTPUT_DIR/index.html"
cat > "$INDEX_FILE" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Reports Index</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #EE0000; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #EE0000; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Compliance Reports Index</h1>
    <p>Generated: DATE_PLACEHOLDER</p>
    <table>
        <thead>
            <tr>
                <th>Framework</th>
                <th>Report</th>
                <th>Console Log</th>
            </tr>
        </thead>
        <tbody>
EOF

for framework in "${FRAMEWORKS[@]}"
do
    json_file=$(ls "$OUTPUT_DIR"/${framework}_compliance_report_*.json 2>/dev/null | head -1)
    if [ -n "$json_file" ]; then
        json_basename=$(basename "$json_file")
        echo "            <tr>" >> "$INDEX_FILE"
        echo "                <td>$framework</td>" >> "$INDEX_FILE"
        echo "                <td><a href=\"$json_basename\">JSON Report</a></td>" >> "$INDEX_FILE"
        echo "                <td><a href=\"${framework}_console.log\">Console Log</a></td>" >> "$INDEX_FILE"
        echo "            </tr>" >> "$INDEX_FILE"
    fi
done

cat >> "$INDEX_FILE" << 'EOF'
        </tbody>
    </table>
</body>
</html>
EOF

# Replace date placeholder
sed -i.bak "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$INDEX_FILE"
rm "$INDEX_FILE.bak" 2>/dev/null || true

echo "Index file created: $INDEX_FILE"
echo "Open in browser: open $INDEX_FILE"
echo ""

exit 0
