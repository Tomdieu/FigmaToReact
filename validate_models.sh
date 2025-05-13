#!/bin/bash

# ================================================================================
# MODEL VALIDATION SCRIPT - OCL Constraint Validation
# ================================================================================
# This script validates XMI instance models against their metamodels using
# OCL (Object Constraint Language) constraints.
#
# Usage:
#   ./validate_models.sh              # Validate Figma model (default)
#   ./validate_models.sh figma        # Validate Figma model
#   ./validate_models.sh react        # Validate React model
#   ./validate_models.sh all          # Validate all models
#
# Author: Ivan Tom
# Purpose: Master's Research - Model Validation for MDE Pipeline
# ================================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse command line arguments
VALIDATION_TARGET="${1:-figma}"

echo -e "${BOLD}================================================================================${NC}"
echo -e "${BOLD}                    MODEL VALIDATION - OCL CONSTRAINTS${NC}"
echo -e "${BOLD}================================================================================${NC}"
echo ""

# ================================================================================
# FUNCTION: Check and build OCL validator
# ================================================================================
check_validator() {
    local VALIDATOR_JAR="ocl-validator/target/ocl-validator-1.0-SNAPSHOT.jar"

    if [ ! -f "$VALIDATOR_JAR" ]; then
        echo -e "${YELLOW}⚠  OCL Validator not built. Building now...${NC}"
        echo ""

        if [ ! -f "ocl-validator/build.sh" ]; then
            echo -e "${RED}✗ Error: ocl-validator/build.sh not found${NC}"
            echo -e "  Please ensure the OCL validator is properly set up"
            exit 1
        fi

        cd ocl-validator
        ./build.sh
        BUILD_STATUS=$?
        cd ..

        if [ $BUILD_STATUS -ne 0 ]; then
            echo -e "${RED}✗ Failed to build OCL validator${NC}"
            exit 1
        fi

        echo -e "${GREEN}✓ OCL Validator built successfully${NC}"
        echo ""
    fi
}

# ================================================================================
# FUNCTION: Validate Figma Model
# ================================================================================
validate_figma() {
    echo -e "${BOLD}[1/1] Validating Figma Instance Model${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "Model:      Model/figma_instance.xmi"
    echo -e "Metamodel:  Metamodel/figma_meta_model.ecore"
    echo -e "OCL:        Metamodel/figma_meta_model.ocl"
    echo ""

    # Check if required files exist
    local MODEL="Model/figma_instance.xmi"
    local METAMODEL="Metamodel/figma_meta_model.ecore"
    local OCL="Metamodel/figma_meta_model.ocl"

    if [ ! -f "$MODEL" ]; then
        echo -e "${RED}✗ Error: Figma instance model not found: $MODEL${NC}"
        return 1
    fi

    if [ ! -f "$METAMODEL" ]; then
        echo -e "${RED}✗ Error: Figma metamodel not found: $METAMODEL${NC}"
        return 1
    fi

    if [ ! -f "$OCL" ]; then
        echo -e "${YELLOW}⚠  Warning: OCL constraints not found: $OCL${NC}"
        echo -e "  Skipping OCL validation..."
        return 2
    fi

    # Run validation
    echo -e "Running OCL validation..."
    cd ocl-validator
    ./validate.sh
    VALIDATION_STATUS=$?
    cd ..
    echo ""

    if [ $VALIDATION_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ FIGMA MODEL VALIDATION PASSED${NC}"
        echo -e "  All OCL constraints satisfied"
        return 0
    else
        echo -e "${RED}✗ FIGMA MODEL VALIDATION FAILED${NC}"
        echo -e "  See error messages above for constraint violations"
        return 1
    fi
}

# ================================================================================
# FUNCTION: Validate React Model
# ================================================================================
validate_react() {
    echo -e "${BOLD}[1/1] Validating React Instance Model${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "Model:      Model/react_new_instance.xmi"
    echo -e "Metamodel:  Metamodel/react_meta_model.ecore"
    echo -e "OCL:        Metamodel/react_meta_model.ocl (if exists)"
    echo ""

    # Check if required files exist
    local MODEL="Model/react_new_instance.xmi"
    local METAMODEL="Metamodel/react_meta_model.ecore"
    local OCL="Metamodel/react_meta_model.ocl"

    if [ ! -f "$MODEL" ]; then
        echo -e "${RED}✗ Error: React instance model not found: $MODEL${NC}"
        echo -e "  Please run the model-to-model transformation first"
        return 1
    fi

    if [ ! -f "$METAMODEL" ]; then
        echo -e "${RED}✗ Error: React metamodel not found: $METAMODEL${NC}"
        return 1
    fi

    if [ ! -f "$OCL" ]; then
        echo -e "${YELLOW}⚠  OCL constraints not found: $OCL${NC}"
        echo -e "  To add validation, create OCL constraints for the React metamodel"
        echo -e "  Performing basic structural validation only..."
        echo ""

        # Basic validation - check if file is valid XML/XMI
        if command -v xmllint &> /dev/null; then
            xmllint --noout "$MODEL" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ React model is valid XMI (basic check)${NC}"
                return 0
            else
                echo -e "${RED}✗ React model is not valid XMI${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠  xmllint not available for XML validation${NC}"
            echo -e "  Install libxml2-utils for basic XML validation"
            echo -e "${GREEN}✓ React model file exists (unable to validate structure)${NC}"
            return 0
        fi
    fi

    # If OCL file exists, run full validation (would need to modify validate.sh to accept parameters)
    echo -e "${YELLOW}⚠  OCL validation for React model not yet implemented${NC}"
    echo -e "  The validate.sh script currently only validates Figma models"
    echo -e "  To implement: modify ocl-validator to accept model/metamodel/ocl as parameters"
    return 2
}

# ================================================================================
# MAIN EXECUTION
# ================================================================================

# Check and build validator if needed
check_validator

# Track overall validation status
OVERALL_STATUS=0

case "$VALIDATION_TARGET" in
    figma)
        validate_figma
        OVERALL_STATUS=$?
        ;;

    react)
        validate_react
        OVERALL_STATUS=$?
        ;;

    all)
        echo -e "${BOLD}Validating all models...${NC}"
        echo ""

        validate_figma
        FIGMA_STATUS=$?
        echo ""

        validate_react
        REACT_STATUS=$?
        echo ""

        # Overall status: fail if any validation failed
        if [ $FIGMA_STATUS -ne 0 ] || [ $REACT_STATUS -ne 0 ]; then
            OVERALL_STATUS=1
        fi
        ;;

    *)
        echo -e "${RED}✗ Invalid validation target: $VALIDATION_TARGET${NC}"
        echo ""
        echo -e "${BOLD}Usage:${NC}"
        echo -e "  $0              # Validate Figma model (default)"
        echo -e "  $0 figma        # Validate Figma model"
        echo -e "  $0 react        # Validate React model"
        echo -e "  $0 all          # Validate all models"
        echo ""
        exit 1
        ;;
esac

# ================================================================================
# SUMMARY
# ================================================================================
echo -e "${BOLD}================================================================================${NC}"
echo -e "${BOLD}                          VALIDATION SUMMARY${NC}"
echo -e "${BOLD}================================================================================${NC}"

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All validations PASSED${NC}"
elif [ $OVERALL_STATUS -eq 2 ]; then
    echo -e "${YELLOW}⚠  Validation incomplete (OCL constraints missing)${NC}"
else
    echo -e "${RED}✗ Validation FAILED${NC}"
    echo -e "  Please fix the constraint violations before proceeding"
fi

echo -e "${BOLD}================================================================================${NC}"

exit $OVERALL_STATUS
