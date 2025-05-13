#!/bin/bash

echo "=========================================="
echo "Building OCL Validator"
echo "=========================================="

cd "$(dirname "$0")"

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed!"
    echo "Please install Maven first:"
    echo "  sudo apt-get install -y maven"
    exit 1
fi

# Build the project
echo "Running Maven build..."
mvn clean package

BUILD_STATUS=$?

if [ $BUILD_STATUS -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Build successful!"
    echo "=========================================="
    echo "JAR file created at:"
    echo "  target/ocl-validator-1.0-SNAPSHOT.jar"
    echo ""
    echo "To run the validator:"
    echo "  ./validate.sh"
else
    echo ""
    echo "Build failed! Please check the errors above."
    exit 1
fi
