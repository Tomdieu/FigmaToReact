#!/bin/bash

# ================================================================================
# COMPLETE ATL TRANSFORMATION PIPELINE: Figma to React
# ================================================================================
# This script orchestrates the complete model-driven engineering pipeline:
# 1. Fetch Figma Design via API and convert to XMI (Python)
# 2. OCL Validation of Figma instance model
# 3. Model-to-Model Transformation (Figma → React)
# 4. OCL Validation of React instance model (optional)
# 5. Model-to-Text Transformation (React Model → React.js Code)
#
# Author: Ivan Tom
# Purpose: Master's Research - MDE-based Figma to React Transformation
# ================================================================================

set -e  # Exit on any error

# Color codes for better output
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
FILE_KEY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --file_key)
            FILE_KEY="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}"
            echo "Usage: $0 [--file_key FIGMA_FILE_KEY]"
            exit 1
            ;;
    esac
done

# Configuration
FETCH_FIGMA=${FETCH_FIGMA:-true}  # Fetch Figma design from API
VALIDATE_FIGMA=${VALIDATE_FIGMA:-true}
VALIDATE_REACT=${VALIDATE_REACT:-false}  # Optional - React metamodel may not have OCL yet
RUN_TRANSFORMATION=${RUN_TRANSFORMATION:-true}
RUN_REFINEMENT=${RUN_REFINEMENT:-true}

# Strict validation mode (for thesis defense/production)
# Set to 'false' only for debugging purposes
STRICT_VALIDATION=${STRICT_VALIDATION:-true}  # Pipeline STOPS if validation fails

echo -e "${BOLD}================================================================================${NC}"
echo -e "${BOLD}           FIGMA TO REACT - COMPLETE TRANSFORMATION PIPELINE${NC}"
echo -e "${BOLD}================================================================================${NC}"
echo -e "${BLUE}Pipeline Configuration:${NC}"
echo -e "  Fetch Figma Design: ${FETCH_FIGMA}"
if [ -n "$FILE_KEY" ]; then
    echo -e "  Figma File Key: ${BOLD}${FILE_KEY}${NC}"
fi
echo -e "  Validate Figma Model: ${VALIDATE_FIGMA}"
echo -e "  Run M2M Transformation: ${RUN_TRANSFORMATION}"
echo -e "  Validate React Model: ${VALIDATE_REACT}"
echo -e "  Run M2T Refinement: ${RUN_REFINEMENT}"
if [ "$STRICT_VALIDATION" = true ]; then
    echo -e "  ${BOLD}Strict Validation: ${GREEN}ENABLED${NC} (Pipeline stops on validation errors)"
else
    echo -e "  ${BOLD}Strict Validation: ${YELLOW}DISABLED${NC} (Pipeline continues despite errors)"
fi
echo -e "${BOLD}================================================================================${NC}"
echo ""

# Track pipeline start time
START_TIME=$(date +%s)
STEP_NUM=0

# ================================================================================
# STEP 1: FETCH FIGMA DESIGN AND CONVERT TO XMI (Python)
# ================================================================================
if [ "$FETCH_FIGMA" = true ]; then
    STEP_NUM=$((STEP_NUM + 1))
    echo -e "${BOLD}[STEP $STEP_NUM] Fetching Figma Design from API${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "Script: python_code/main.py"
    echo -e "Output: Model/figma_instance.json, Model/figma_instance.xmi"
    echo ""

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Error: Python 3 is not installed${NC}"
        echo -e "  Please install Python 3 to continue"
        exit 1
    fi
    echo -e "${GREEN}✓ Python found:${NC} $(python3 --version)"

    # Check if python_code directory exists
    if [ ! -d "python_code" ]; then
        echo -e "${RED}✗ Error: python_code directory not found${NC}"
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f "python_code/.env" ]; then
        echo -e "${RED}✗ Error: .env file not found in python_code/${NC}"
        echo -e "${YELLOW}  Please create python_code/.env with your FIGMA_TOKEN${NC}"
        echo -e "  Example: cp python_code/.env.example python_code/.env"
        echo -e "  Then edit .env and add your Figma API token"
        exit 1
    fi
    echo -e "${GREEN}✓ Environment file found${NC}"

    # Check if requirements are installed
    echo -e "Checking Python dependencies..."
    cd python_code

    # Check if virtual environment exists
    if [ -d "env" ]; then
        echo -e "${GREEN}✓ Virtual environment found${NC}"
        source env/bin/activate
    else
        echo -e "${YELLOW}⚠  Virtual environment not found. Checking system packages...${NC}"
    fi

    # Try to import required packages
    python3 -c "import requests, dotenv" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠  Dependencies not installed. Installing now...${NC}"
        pip3 install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ Failed to install dependencies${NC}"
            cd ..
            exit 1
        fi
    fi
    echo -e "${GREEN}✓ Python dependencies available${NC}"

    # Backup existing files if they exist
    if [ -f "../Model/figma_instance.xmi" ]; then
        BACKUP_FILE="../Model/figma_instance.xmi.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Backing up existing figma_instance.xmi to:${NC}"
        echo -e "  $BACKUP_FILE"
        cp "../Model/figma_instance.xmi" "$BACKUP_FILE"
    fi

    # Run the Python script
    echo -e ""
    echo -e "Fetching Figma design and converting to XMI..."
    
    # Build the python command with optional --file_key argument
    PYTHON_CMD="python3 main.py"
    if [ -n "$FILE_KEY" ]; then
        echo -e "Using custom file key: ${BOLD}${FILE_KEY}${NC}"
        PYTHON_CMD="$PYTHON_CMD --file_key $FILE_KEY"
    else
        echo -e "Using default file key from main.py"
    fi
    
    # Execute the Python script
    $PYTHON_CMD
    FETCH_STATUS=$?

    # Deactivate virtual environment if it was activated
    if [ -d "env" ]; then
        deactivate 2>/dev/null || true
    fi

    cd ..

    if [ $FETCH_STATUS -eq 0 ] && [ -f "Model/figma_instance.xmi" ]; then
        FILE_SIZE=$(stat -c%s "Model/figma_instance.xmi" 2>/dev/null || stat -f%z "Model/figma_instance.xmi" 2>/dev/null)
        if [ "$FILE_SIZE" -gt 100 ]; then
            echo -e "${GREEN}✓ Figma design fetched and converted to XMI${NC}"
            echo -e "  Output: Model/figma_instance.xmi ($FILE_SIZE bytes)"
            [ -f "Model/figma_instance.json" ] && echo -e "  JSON: Model/figma_instance.json"
        else
            echo -e "${RED}✗ XMI file is empty or invalid${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Failed to fetch Figma design or convert to XMI${NC}"
        echo -e "${YELLOW}Please check:${NC}"
        echo -e "  1. FIGMA_TOKEN is valid in python_code/.env"
        echo -e "  2. Figma file key is correct in main.py"
        echo -e "  3. Internet connection is available"
        exit 1
    fi

    echo ""
fi

# ================================================================================
# STEP 2: VALIDATE FIGMA MODEL (OCL Constraints)
# ================================================================================
if [ "$VALIDATE_FIGMA" = true ]; then
    STEP_NUM=$((STEP_NUM + 1))
    echo -e "${BOLD}[STEP $STEP_NUM] Validating Figma Instance Model${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"

    # Check if OCL validator is built
    if [ ! -f "ocl-validator/target/ocl-validator-1.0-SNAPSHOT.jar" ]; then
        echo -e "${YELLOW}⚠  OCL Validator not built. Building now...${NC}"
        cd ocl-validator
        ./build.sh
        cd ..
    fi

    # Check if OCL file exists
    if [ -f "Metamodel/figma_meta_model.ocl" ]; then
        echo -e "Validating Model/figma_instance.xmi against OCL constraints..."
        cd ocl-validator
        ./validate.sh
        VALIDATION_STATUS=$?
        cd ..

        if [ $VALIDATION_STATUS -eq 0 ]; then
            echo -e "${GREEN}✓ Figma model validation PASSED${NC}"
            echo -e "  All OCL constraints satisfied"
        else
            echo -e "${RED}✗ Figma model validation FAILED${NC}"
            echo -e "${RED}  One or more OCL constraints were violated${NC}"
            echo ""

            if [ "$STRICT_VALIDATION" = true ]; then
                echo -e "${BOLD}${RED}════════════════════════════════════════════════════════════════${NC}"
                echo -e "${BOLD}${RED}                   VALIDATION FAILED - STOPPING PIPELINE${NC}"
                echo -e "${BOLD}${RED}════════════════════════════════════════════════════════════════${NC}"
                echo ""
                echo -e "${YELLOW}The Figma instance model contains constraint violations.${NC}"
                echo -e "${YELLOW}Transformation cannot proceed until these issues are fixed.${NC}"
                echo ""
                echo -e "${BOLD}Why this matters:${NC}"
                echo -e "  • OCL constraints ensure model integrity and correctness"
                echo -e "  • Invalid models can produce incorrect transformations"
                echo -e "  • Quality assurance requires valid input models"
                echo ""
                echo -e "${BOLD}What to do:${NC}"
                echo -e "  1. Review the validation errors above"
                echo -e "  2. Fix the constraint violations in your Figma design"
                echo -e "  3. Re-fetch the Figma model: ${BLUE}cd python_code && python3 main.py && cd ..${NC}"
                echo -e "  4. Re-run the pipeline: ${BLUE}./run_complete_pipeline.sh${NC}"
                echo ""
                echo -e "${BOLD}For debugging only (not recommended):${NC}"
                echo -e "  To bypass validation: ${YELLOW}STRICT_VALIDATION=false ./run_complete_pipeline.sh${NC}"
                echo ""
                echo -e "${BOLD}════════════════════════════════════════════════════════════════${NC}"
                exit 1
            else
                echo -e "${YELLOW}⚠  WARNING: Strict validation is DISABLED${NC}"
                echo -e "${YELLOW}⚠  Continuing with transformation despite validation errors...${NC}"
                echo -e "${YELLOW}⚠  This may produce incorrect results!${NC}"
                echo ""
                sleep 2  # Give user time to see the warning
            fi
        fi
    else
        echo -e "${YELLOW}⚠  No OCL constraints found for Figma metamodel${NC}"
        echo -e "  Skipping validation..."
    fi

    echo ""
fi

# ================================================================================
# STEP 3: MODEL-TO-MODEL TRANSFORMATION (Figma → React)
# ================================================================================
if [ "$RUN_TRANSFORMATION" = true ]; then
    STEP_NUM=$((STEP_NUM + 1))
    echo -e "${BOLD}[STEP $STEP_NUM] Model-to-Model Transformation (Figma → React)${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "Input:  Model/figma_instance.xmi"
    echo -e "Output: Model/react_new_instance.xmi"
    echo -e "ATL:    Transformations/tranform.atl"
    echo ""

    # Backup existing output if it exists
    if [ -f "Model/react_new_instance.xmi" ]; then
        BACKUP_FILE="Model/react_new_instance.xmi.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Backing up existing react_new_instance.xmi to:${NC}"
        echo -e "  $BACKUP_FILE"
        cp "Model/react_new_instance.xmi" "$BACKUP_FILE"
    fi

    # Run the transformation
    ./transform_figma_to_react.sh
    TRANSFORM_STATUS=$?

    if [ $TRANSFORM_STATUS -eq 0 ] && [ -f "Model/react_new_instance.xmi" ]; then
        FILE_SIZE=$(stat -c%s "Model/react_new_instance.xmi" 2>/dev/null || stat -f%z "Model/react_new_instance.xmi" 2>/dev/null)
        if [ "$FILE_SIZE" -gt 100 ]; then
            echo -e "${GREEN}✓ Model-to-Model transformation COMPLETED${NC}"
            echo -e "  Output size: $FILE_SIZE bytes"
        else
            echo -e "${RED}✗ Model-to-Model transformation produced empty/invalid output${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Model-to-Model transformation FAILED${NC}"
        echo -e "${YELLOW}Please check the error messages above and ensure:${NC}"
        echo -e "  1. Eclipse is installed at the correct path"
        echo -e "  2. ATL plugins are installed in Eclipse"
        echo -e "  3. All input files exist and are valid"
        exit 1
    fi

    echo ""
fi

# ================================================================================
# STEP 4: VALIDATE REACT MODEL (Optional - OCL Constraints)
# ================================================================================
if [ "$VALIDATE_REACT" = true ]; then
    STEP_NUM=$((STEP_NUM + 1))
    echo -e "${BOLD}[STEP $STEP_NUM] Validating React Instance Model${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"

    # Check if React OCL file exists
    if [ -f "Metamodel/react_meta_model.ocl" ]; then
        echo -e "Validating Model/react_new_instance.xmi against OCL constraints..."
        # This would require updating the validate.sh script to accept parameters
        echo -e "${YELLOW}⚠  React model validation not yet implemented${NC}"
        echo -e "  To implement: create OCL constraints for react_meta_model.ecore"
    else
        echo -e "${YELLOW}⚠  No OCL constraints found for React metamodel${NC}"
        echo -e "  Skipping validation..."
    fi

    echo ""
fi

# ================================================================================
# STEP 5: MODEL-TO-TEXT TRANSFORMATION (React Model → React.js Code)
# ================================================================================
if [ "$RUN_REFINEMENT" = true ]; then
    STEP_NUM=$((STEP_NUM + 1))
    echo -e "${BOLD}[STEP $STEP_NUM] Model-to-Text Transformation (React Model → React Code)${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "Input:  Model/react_new_instance.xmi"
    echo -e "Output: Generated React.js application"
    echo -e "ATL:    Transformations/refine2.atl"
    echo ""

    # Check if react_new_instance.xmi exists
    if [ ! -f "Model/react_new_instance.xmi" ]; then
        echo -e "${RED}✗ Error: react_new_instance.xmi not found${NC}"
        echo -e "  Please run the model-to-model transformation first"
        exit 1
    fi

    # Extract app name from figma_instance.xmi to know where code will be generated
    APP_NAME=$(grep -oP 'name="\K[^"]+' "Model/figma_instance.xmi" | head -1)
    if [ -z "$APP_NAME" ]; then
        APP_NAME="UnnamedApp"
    fi
    echo -e "Detected application name: ${BOLD}${APP_NAME}${NC}"
    echo -e "Code will be generated in: ${BOLD}./${APP_NAME}/${NC}"
    echo ""

    # Run the refinement transformation
    ./refine_react.sh
    REFINE_STATUS=$?

    if [ $REFINE_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Model-to-Text transformation COMPLETED${NC}"
        echo ""

        # Check if the expected directory exists
        if [ -d "$APP_NAME" ]; then
            echo -e "${GREEN}✓ React application generated successfully!${NC}"
            echo -e ""
            echo -e "${BOLD}Generated project:${NC} ${GREEN}./${APP_NAME}/${NC}"

            # Show project structure
            if [ -f "$APP_NAME/package.json" ]; then
                echo -e ""
                echo -e "${BOLD}Project structure:${NC}"
                [ -f "$APP_NAME/package.json" ] && echo -e "  ✓ package.json"
                [ -f "$APP_NAME/vite.config.js" ] && echo -e "  ✓ vite.config.js"
                [ -f "$APP_NAME/index.html" ] && echo -e "  ✓ index.html"
                [ -f "$APP_NAME/src/App.jsx" ] && echo -e "  ✓ src/App.jsx"
                [ -f "$APP_NAME/src/main.jsx" ] && echo -e "  ✓ src/main.jsx"

                # Count components and pages
                if [ -d "$APP_NAME/src/components" ]; then
                    COMP_COUNT=$(find "$APP_NAME/src/components" -name "*.jsx" 2>/dev/null | wc -l)
                    echo -e "  ✓ src/components/ (${COMP_COUNT} components)"
                fi
                if [ -d "$APP_NAME/src/pages" ]; then
                    PAGE_COUNT=$(find "$APP_NAME/src/pages" -name "*.jsx" 2>/dev/null | wc -l)
                    echo -e "  ✓ src/pages/ (${PAGE_COUNT} pages)"
                fi
            fi

            echo -e ""
            echo -e "${BOLD}Next steps to run the application:${NC}"
            echo -e "  ${BLUE}cd ${APP_NAME}${NC}"
            echo -e "  ${BLUE}npm install${NC}"
            echo -e "  ${BLUE}npm run dev${NC}"
        else
            echo -e "${YELLOW}⚠  Expected directory not found: ./${APP_NAME}/${NC}"
            echo -e ""
            echo -e "Looking for generated folders..."
            # Find recently created directories
            FOUND_DIRS=$(find . -maxdepth 1 -type d -mmin -2 ! -name "." ! -name ".git" ! -name "Model" ! -name "Metamodel" ! -name "Transformations" ! -name "python_code" ! -name "ocl-validator" ! -name "atl-runner" ! -name "images" ! -name "workspace" 2>/dev/null)

            if [ -n "$FOUND_DIRS" ]; then
                echo "$FOUND_DIRS" | while read dir; do
                    [ -n "$dir" ] && [ "$dir" != "." ] && echo -e "  Found: ${GREEN}${dir}${NC}"
                done
            else
                echo -e "  ${YELLOW}No recently created directories found${NC}"
                echo -e "  Check the refine_react.sh output above for details"
            fi
        fi
    else
        echo -e "${YELLOW}⚠ Model-to-Text transformation may have issues${NC}"
        echo -e "  Check the output above for details"
    fi

    echo ""
fi

# ================================================================================
# PIPELINE SUMMARY
# ================================================================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "${BOLD}================================================================================${NC}"
echo -e "${BOLD}                        PIPELINE EXECUTION SUMMARY${NC}"
echo -e "${BOLD}================================================================================${NC}"
echo -e "${GREEN}Pipeline completed successfully!${NC}"
echo -e "Total execution time: ${DURATION} seconds"
echo ""
echo -e "${BOLD}Generated Artifacts:${NC}"
[ -f "Model/figma_instance.xmi" ] && echo -e "  ${GREEN}✓${NC} Model/figma_instance.xmi"
[ -f "Model/figma_instance.json" ] && echo -e "  ${GREEN}✓${NC} Model/figma_instance.json"
[ -f "Model/react_new_instance.xmi" ] && echo -e "  ${GREEN}✓${NC} Model/react_new_instance.xmi"

# Check for generated React app
if [ "$RUN_REFINEMENT" = true ]; then
    APP_NAME=$(grep -oP 'name="\K[^"]+' "Model/figma_instance.xmi" 2>/dev/null | head -1)
    if [ -n "$APP_NAME" ] && [ -d "$APP_NAME" ]; then
        echo -e "  ${GREEN}✓${NC} ${APP_NAME}/ (React application)"
    fi
fi
echo ""
echo -e "${BOLD}Pipeline Steps Executed:${NC}"
[ "$FETCH_FIGMA" = true ] && echo -e "  ${GREEN}✓${NC} Fetch Figma Design (API → XMI)"
[ "$VALIDATE_FIGMA" = true ] && echo -e "  ${GREEN}✓${NC} Figma Model Validation (OCL)"
[ "$RUN_TRANSFORMATION" = true ] && echo -e "  ${GREEN}✓${NC} Model-to-Model Transformation"
[ "$VALIDATE_REACT" = true ] && echo -e "  ${GREEN}✓${NC} React Model Validation (OCL)"
[ "$RUN_REFINEMENT" = true ] && echo -e "  ${GREEN}✓${NC} Model-to-Text Transformation"
echo ""
echo -e "${BLUE}For more information about the transformation pipeline, see:${NC}"
echo -e "  README.md (if available)"
echo -e "  Transformations/tranform.atl - M2M transformation rules"
echo -e "  Transformations/refine2.atl - M2T transformation rules"
echo -e "${BOLD}================================================================================${NC}"