#!/bin/bash

# ATL Model-to-Text Transformation: React Model Refinement
# This script refines react_new_instance.xmi and generates React code

echo "================================================================================"
echo "ATL Model-to-Text Transformation: React Refinement"
echo "================================================================================"

# Paths
ECLIPSE_HOME="/home/ivantom/tool/eclipse"
WORKSPACE="/home/ivantom/design2code/FigmaToReact"
ATL_FILE="$WORKSPACE/Transformations/refine2.atl"
SOURCE_MODEL="$WORKSPACE/Model/react_new_instance.xmi"
METAMODEL="$WORKSPACE/Metamodel/react_meta_model.ecore"

# Check if files exist
echo ""
echo "[1/4] Checking input files..."

if [ ! -f "$ATL_FILE" ]; then
    echo "    ✗ Error: ATL transformation file not found: $ATL_FILE"
    exit 1
fi
echo "    ✓ ATL transformation: $ATL_FILE"

if [ ! -f "$SOURCE_MODEL" ]; then
    echo "    ✗ Error: Source model not found: $SOURCE_MODEL"
    echo "    Please run transform_figma_to_react.sh first"
    exit 1
fi
echo "    ✓ Source model: $SOURCE_MODEL"

if [ ! -f "$METAMODEL" ]; then
    echo "    ✗ Error: Metamodel not found: $METAMODEL"
    exit 1
fi
echo "    ✓ Metamodel: $METAMODEL"

# Check if Eclipse is installed
echo ""
echo "[2/4] Checking Eclipse installation..."
if [ ! -d "$ECLIPSE_HOME" ]; then
    echo "    ✗ Error: Eclipse not found at $ECLIPSE_HOME"
    exit 1
fi

ECLIPSE_LAUNCHER=$(find "$ECLIPSE_HOME/plugins" -name "org.eclipse.equinox.launcher_*.jar" | head -1)
if [ -z "$ECLIPSE_LAUNCHER" ]; then
    echo "    ✗ Error: Eclipse launcher not found"
    exit 1
fi
echo "    ✓ Eclipse found: $ECLIPSE_HOME"

# Check for ATL plugin
ATL_ENGINE=$(find "$ECLIPSE_HOME/plugins" -name "org.eclipse.m2m.atl.engine.emfvm_*.jar" | head -1)
if [ -z "$ATL_ENGINE" ]; then
    echo "    ✗ Error: ATL engine not found in Eclipse plugins"
    echo "    Please install ATL from Eclipse Marketplace"
    exit 1
fi
echo "    ✓ ATL engine found"

# Extract app name from figma_instance.xmi
echo ""
echo "[3/4] Detecting application name..."
APP_NAME=$(grep -oP 'name="\K[^"]+' "$WORKSPACE/Model/figma_instance.xmi" | head -1)
if [ -z "$APP_NAME" ]; then
    APP_NAME="UnnamedApp"
fi
echo "    Application name: $APP_NAME"
echo "    React code will be generated in: $WORKSPACE/$APP_NAME/"

# Run transformation (query)
echo ""
echo "[4/4] Running ATL query (model-to-text)..."
echo "    This transformation will generate React code files"
echo ""

# Since refine2.atl is a query (model-to-text), we need to run it differently
# ATL queries don't produce XMI but generate text files directly

echo "    ⚠ Note: refine2.atl is a query-based transformation"
echo "    It generates text files directly rather than XMI models"
echo ""

# Try to run as ATL query
java -jar "$ECLIPSE_LAUNCHER" \
    -application org.eclipse.m2m.atl.engine.emfvm.launch \
    -data "$WORKSPACE/workspace" \
    -source "$SOURCE_MODEL" \
    -metamodel "$METAMODEL" \
    -query "$ATL_FILE" \
    -nosplash -consoleLog 2>&1

TRANSFORM_STATUS=$?

# Check results
echo ""
echo "================================================================================"

if [ $TRANSFORM_STATUS -eq 0 ]; then
    echo "QUERY EXECUTION COMPLETED"
    echo "================================================================================"
    echo ""
    echo "The ATL query has been executed."
    echo ""

    # Check for the generated project directory
    PROJECT_DIR="$WORKSPACE/$APP_NAME"
    if [ -d "$PROJECT_DIR" ]; then
        echo "✓ React application generated successfully!"
        echo ""
        echo "Generated project: $PROJECT_DIR"
        echo ""

        # Show generated file structure
        if [ -f "$PROJECT_DIR/package.json" ]; then
            echo "📦 Project files:"
            [ -f "$PROJECT_DIR/package.json" ] && echo "  ✓ package.json"
            [ -f "$PROJECT_DIR/vite.config.js" ] && echo "  ✓ vite.config.js"
            [ -f "$PROJECT_DIR/index.html" ] && echo "  ✓ index.html"
            echo ""
        fi

        # Count generated components and pages
        if [ -d "$PROJECT_DIR/src" ]; then
            echo "📁 Source files:"
            [ -f "$PROJECT_DIR/src/App.jsx" ] && echo "  ✓ src/App.jsx"
            [ -f "$PROJECT_DIR/src/main.jsx" ] && echo "  ✓ src/main.jsx"

            if [ -d "$PROJECT_DIR/src/components" ]; then
                COMPONENT_COUNT=$(find "$PROJECT_DIR/src/components" -name "*.jsx" 2>/dev/null | wc -l)
                echo "  ✓ src/components/ ($COMPONENT_COUNT components)"
            fi

            if [ -d "$PROJECT_DIR/src/pages" ]; then
                PAGE_COUNT=$(find "$PROJECT_DIR/src/pages" -name "*.jsx" 2>/dev/null | wc -l)
                echo "  ✓ src/pages/ ($PAGE_COUNT pages)"
            fi
            echo ""
        fi

        echo "To run the generated application:"
        echo "  cd $APP_NAME"
        echo "  npm install"
        echo "  npm run dev"
    else
        echo "⚠ Warning: Expected project directory not found: $PROJECT_DIR"
        echo ""
        echo "The refine2.atl query may generate files in a different location."
        echo "Check the current directory for a folder named after your Figma design."
        echo ""
        echo "Looking for generated folders..."
        # List directories created recently (within last minute)
        find "$WORKSPACE" -maxdepth 1 -type d -mmin -1 ! -name "." ! -name ".git" ! -name "Model" ! -name "Metamodel" ! -name "Transformations" ! -name "python_code" ! -name "ocl-validator" ! -name "atl-runner" ! -name "images" ! -name "workspace" 2>/dev/null | while read dir; do
            if [ "$dir" != "$WORKSPACE" ]; then
                echo "  Found: $dir"
            fi
        done
    fi
else
    echo "TRANSFORMATION MAY HAVE ISSUES"
    echo "================================================================================"
    echo ""
    echo "The transformation could not be completed using the command-line method."
    echo ""
    echo "ALTERNATIVE METHOD - Use Eclipse IDE:"
    echo ""
    echo "1. Open Eclipse"
    echo "2. Import the project: File → Import → Existing Projects into Workspace"
    echo "3. Open '$ATL_FILE' in Eclipse"
    echo "4. Right-click on the file"
    echo "5. Select: Run As → ATL Query"
    echo "6. Configure:"
    echo "   - Source model: $SOURCE_MODEL"
    echo "   - Metamodel: $METAMODEL"
    echo ""
    echo "The query will generate React.js source code files based on the model."
    echo ""
fi

echo "================================================================================"
