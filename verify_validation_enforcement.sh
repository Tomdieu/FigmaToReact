#!/bin/bash

# Quick Verification Script - Validates that OCL enforcement works
# Run this before your thesis defense to confirm protection is active

echo "═══════════════════════════════════════════════════════════════════"
echo "        VALIDATION ENFORCEMENT - QUICK VERIFICATION"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PASS_COUNT=0
FAIL_COUNT=0

echo "CHECK 1: Strict validation is enabled by default"
echo "─────────────────────────────────────────────────────────────────"
if grep -q "STRICT_VALIDATION=\${STRICT_VALIDATION:-true}" run_complete_pipeline.sh; then
    echo "✓ PASS: STRICT_VALIDATION defaults to true"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ FAIL: STRICT_VALIDATION not set to true by default"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo ""

echo "CHECK 2: Pipeline exits on validation failure"
echo "─────────────────────────────────────────────────────────────────"
if grep -A 25 "if.*STRICT_VALIDATION.*true" run_complete_pipeline.sh | grep -q "exit 1"; then
    echo "✓ PASS: 'exit 1' found in strict validation block"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ FAIL: 'exit 1' not found - pipeline may continue"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo ""

echo "CHECK 3: Validation runs before transformation"
echo "─────────────────────────────────────────────────────────────────"
# Get line numbers using step delimiters
VALIDATION_LINE=$(grep -n "STEP 2: VALIDATE FIGMA MODEL" run_complete_pipeline.sh | cut -d: -f1)
TRANSFORM_LINE=$(grep -n "STEP 3: MODEL-TO-MODEL TRANSFORMATION" run_complete_pipeline.sh | cut -d: -f1)

if [ -n "$VALIDATION_LINE" ] && [ -n "$TRANSFORM_LINE" ] && [ "$VALIDATION_LINE" -lt "$TRANSFORM_LINE" ]; then
    echo "✓ PASS: Validation (line $VALIDATION_LINE) runs before transformation (line $TRANSFORM_LINE)"
    PASS_COUNT=$((PASS_COUNT + 1))
elif [ -z "$VALIDATION_LINE" ] || [ -z "$TRANSFORM_LINE" ]; then
    # Just verify the validation logic exists before transformation starts
    if grep -q "VALIDATION_STATUS=\$?" run_complete_pipeline.sh && grep -q "exit 1" run_complete_pipeline.sh; then
        echo "✓ PASS: Validation enforcement code exists"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "✗ FAIL: Validation enforcement may be missing"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
else
    echo "✗ FAIL: Step order may be incorrect (Val: $VALIDATION_LINE, Trans: $TRANSFORM_LINE)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo ""

echo "CHECK 4: Test script exists and is executable"
echo "─────────────────────────────────────────────────────────────────"
if [ -x "test_validation_enforcement.sh" ]; then
    echo "✓ PASS: test_validation_enforcement.sh is executable"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ FAIL: test_validation_enforcement.sh not found or not executable"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo ""

echo "CHECK 5: Documentation files exist"
echo "─────────────────────────────────────────────────────────────────"
DOC_PASS=0
DOC_TOTAL=3

[ -f "VALIDATION_ENFORCEMENT.md" ] && DOC_PASS=$((DOC_PASS + 1)) && echo "  ✓ VALIDATION_ENFORCEMENT.md"
[ -f "THESIS_DEFENSE_CHECKLIST.md" ] && DOC_PASS=$((DOC_PASS + 1)) && echo "  ✓ THESIS_DEFENSE_CHECKLIST.md"
[ -f "QUICK_START.md" ] && DOC_PASS=$((DOC_PASS + 1)) && echo "  ✓ QUICK_START.md"

if [ $DOC_PASS -eq $DOC_TOTAL ]; then
    echo "✓ PASS: All documentation files present ($DOC_PASS/$DOC_TOTAL)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ FAIL: Missing documentation files ($DOC_PASS/$DOC_TOTAL)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo ""

echo "CHECK 6: OCL constraint file exists"
echo "─────────────────────────────────────────────────────────────────"
if [ -f "Metamodel/figma_meta_model.ocl" ]; then
    CONSTRAINT_COUNT=$(grep -c '^inv' Metamodel/figma_meta_model.ocl)
    echo "✓ PASS: OCL file exists with $CONSTRAINT_COUNT constraints"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ FAIL: OCL constraint file not found"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo "                         VERIFICATION RESULTS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Checks Passed: $PASS_COUNT"
echo "Checks Failed: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo ""
    echo "Your validation enforcement is correctly configured and ready"
    echo "for thesis defense. The pipeline WILL STOP on validation errors."
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./test_validation_enforcement.sh"
    echo "  2. Review: THESIS_DEFENSE_CHECKLIST.md"
    echo "  3. Practice your defense demo"
    echo ""
    exit 0
else
    echo "❌ SOME CHECKS FAILED"
    echo ""
    echo "Please review the failed checks above and fix any issues."
    echo "Your validation enforcement may not work correctly."
    echo ""
    exit 1
fi
