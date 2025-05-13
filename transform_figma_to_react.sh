#!/bin/bash

# ATL Model-to-Model Transformation: Figma to React
# This script transforms figma_instance.xmi to react_new_instance.xmi

echo "================================================================================"
echo "ATL Model-to-Model Transformation: Figma → React"
echo "================================================================================"

# Paths
ECLIPSE_HOME="/home/ivantom/tool/eclipse"
WORKSPACE="/home/ivantom/design2code/FigmaToReact"
ATL_FILE="$WORKSPACE/Transformations/tranform.atl"
SOURCE_MODEL="$WORKSPACE/Model/figma_instance.xmi"
TARGET_MODEL="$WORKSPACE/Model/react_new_instance.xmi"
SOURCE_METAMODEL="$WORKSPACE/Metamodel/figma_meta_model.ecore"
TARGET_METAMODEL="$WORKSPACE/Metamodel/react_meta_model.ecore"

# Check if files exist
echo ""
echo "[1/5] Checking input files..."

if [ ! -f "$ATL_FILE" ]; then
    echo "    ✗ Error: ATL transformation file not found: $ATL_FILE"
    exit 1
fi
echo "    ✓ ATL transformation: $ATL_FILE"

if [ ! -f "$SOURCE_MODEL" ]; then
    echo "    ✗ Error: Source model not found: $SOURCE_MODEL"
    exit 1
fi
echo "    ✓ Source model: $SOURCE_MODEL"

if [ ! -f "$SOURCE_METAMODEL" ]; then
    echo "    ✗ Error: Source metamodel not found: $SOURCE_METAMODEL"
    exit 1
fi
echo "    ✓ Source metamodel: $SOURCE_METAMODEL"

if [ ! -f "$TARGET_METAMODEL" ]; then
    echo "    ✗ Error: Target metamodel not found: $TARGET_METAMODEL"
    exit 1
fi
echo "    ✓ Target metamodel: $TARGET_METAMODEL"

# Check if Eclipse is installed
echo ""
echo "[2/5] Checking Eclipse installation..."
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

# Compile ATL to ASM
echo ""
echo "[3/5] Compiling ATL transformation..."
ASM_FILE="${ATL_FILE%.atl}.asm"

# Use Eclipse ATL compiler
java -jar "$ECLIPSE_LAUNCHER" \
    -application org.eclipse.m2m.atl.core.ATL \
    -data "$WORKSPACE/workspace" \
    -atlfile "$ATL_FILE" \
    -outputfile "$ASM_FILE" \
    -nosplash -consoleLog 2>&1

if [ $? -eq 0 ] && [ -f "$ASM_FILE" ]; then
    echo "    ✓ ATL compiled: $ASM_FILE"
else
    echo "    ⚠ ATL compilation might have issues, but continuing..."
    # ATL file may already be compiled or we'll use the .atl directly
fi

# Run transformation
echo ""
echo "[4/5] Running ATL transformation..."
echo "    Source: figma_instance.xmi → Target: react_new_instance.xmi"

# Try to run using Eclipse application
java -jar "$ECLIPSE_LAUNCHER" \
    -application org.eclipse.m2m.atl.engine.emfvm.launch \
    -data "$WORKSPACE/workspace" \
    -source "$SOURCE_MODEL" \
    -target "$TARGET_MODEL" \
    -sourceMetamodel "$SOURCE_METAMODEL" \
    -targetMetamodel "$TARGET_METAMODEL" \
    -transformation "$ATL_FILE" \
    -nosplash -consoleLog 2>&1

TRANSFORM_STATUS=$?

# Check if transformation was successful
echo ""
echo "[5/5] Checking transformation results..."

if [ -f "$TARGET_MODEL" ]; then
    FILE_SIZE=$(stat -c%s "$TARGET_MODEL" 2>/dev/null || stat -f%z "$TARGET_MODEL" 2>/dev/null)
    if [ "$FILE_SIZE" -gt 100 ]; then
        echo "    ✓ Target model created successfully!"
        echo "    File: $TARGET_MODEL"
        echo "    Size: $FILE_SIZE bytes"
    else
        echo "    ⚠ Target model exists but may be empty or incomplete"
        echo "    Size: $FILE_SIZE bytes"
    fi
else
    echo "    ✗ Target model was not created"
    echo ""
    echo "================================================================================"
    echo "TRANSFORMATION FAILED"
    echo "================================================================================"
    echo ""
    echo "The transformation could not be completed using the command-line method."
    echo "Please use Eclipse IDE to run the transformation:"
    echo ""
    echo "1. Open Eclipse"
    echo "2. Import the project: File → Import → Existing Projects into Workspace"
    echo "3. Right-click on '$ATL_FILE'"
    echo "4. Select: Run As → ATL Transformation"
    echo "5. Configure the transformation with:"
    echo "   - Source model: $SOURCE_MODEL"
    echo "   - Target model: $TARGET_MODEL"
    echo "   - Source metamodel: $SOURCE_METAMODEL"
    echo "   - Target metamodel: $TARGET_METAMODEL"
    echo ""
    echo "================================================================================"
    exit 1
fi

echo ""
echo "================================================================================"
echo "TRANSFORMATION COMPLETED"
echo "================================================================================"
echo "Input:  $SOURCE_MODEL"
echo "Output: $TARGET_MODEL"
echo "================================================================================"
