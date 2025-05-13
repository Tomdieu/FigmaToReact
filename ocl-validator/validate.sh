#!/bin/bash

cd "$(dirname "$0")"

# Paths to your files
MODEL="../Model/figma_instance.xmi"
METAMODEL="../Metamodel/figma_meta_model.ecore"
OCL="../Metamodel/figma_meta_model.ocl"
JAR="target/ocl-validator-1.0-SNAPSHOT.jar"

# Check if JAR exists
if [ ! -f "$JAR" ]; then
    echo "Error: Validator JAR not found!"
    echo "Please run ./build.sh first to build the validator."
    exit 1
fi

# Check if input files exist
if [ ! -f "$MODEL" ]; then
    echo "Error: Model file not found: $MODEL"
    exit 1
fi

if [ ! -f "$METAMODEL" ]; then
    echo "Error: Metamodel file not found: $METAMODEL"
    exit 1
fi

if [ ! -f "$OCL" ]; then
    echo "Error: OCL file not found: $OCL"
    exit 1
fi

# Run the validator
java -jar "$JAR" "$MODEL" "$METAMODEL" "$OCL"
