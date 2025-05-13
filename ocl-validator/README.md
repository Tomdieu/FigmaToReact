# OCL Model Validator

A Java application to validate XMI model instances against OCL constraints defined in Ecore metamodels.

## Prerequisites

- Java 17 or higher
- Maven (for building)

### Install Maven

```bash
sudo apt-get update
sudo apt-get install maven
```

## Building

To build the validator, run:

```bash
./build.sh
```

This will create a standalone JAR file: `target/ocl-validator-1.0-SNAPSHOT.jar`

## Usage

### Quick Start

To validate your Figma model with the pre-configured paths:

```bash
./validate.sh
```

This script validates:
- Model: `../Model/figma_instance.xmi`
- Metamodel: `../Metamodel/figma_meta_model.ecore`
- OCL Constraints: `../Metamodel/figma_meta_model.ocl`

### Manual Execution

You can also run the validator manually with custom paths:

```bash
java -jar target/ocl-validator-1.0-SNAPSHOT.jar <model.xmi> <metamodel.ecore> <constraints.ocl>
```

**Example:**

```bash
java -jar target/ocl-validator-1.0-SNAPSHOT.jar \
    ../Model/figma_instance.xmi \
    ../Metamodel/figma_meta_model.ecore \
    ../Metamodel/figma_meta_model.ocl
```

## Output

The validator will:
1. Load the metamodel (Ecore file)
2. Load the model instance (XMI file)
3. Parse OCL constraints
4. Validate the model against the constraints
5. Display a summary of errors and warnings

### Exit Codes

- `0`: Validation successful (no errors)
- `1`: Validation failed (constraints violated)
- `2`: Runtime error (file not found, parsing error, etc.)

## Example Output

```
================================================================================
OCL Model Validator
================================================================================
Model file:      ../Model/figma_instance.xmi
Metamodel file:  ../Metamodel/figma_meta_model.ecore
OCL file:        ../Metamodel/figma_meta_model.ocl
================================================================================

[1/4] Loading metamodel...
    ✓ Metamodel loaded: figma_meta_model

[2/4] Loading model instance...
    ✓ Model loaded with 1 root element(s)

[3/4] Parsing OCL constraints...
    ✓ Found 45 OCL constraints

[4/4] Validating model...

================================================================================
VALIDATION RESULTS
================================================================================
✓ Model is VALID - All constraints satisfied!

No errors or warnings found.
================================================================================
```

## Project Structure

```
ocl-validator/
├── pom.xml                  # Maven configuration
├── build.sh                 # Build script
├── validate.sh              # Validation script
├── README.md               # This file
└── src/
    └── main/
        └── java/
            └── com/
                └── figma/
                    └── validator/
                        └── OCLValidator.java
```

## Dependencies

- Eclipse EMF (Ecore, XMI)
- Eclipse OCL
- Eclipse Platform Runtime

All dependencies are automatically downloaded by Maven during the build process.

## Notes

**Important:** This validator uses EMF's built-in validation mechanism. For the OCL constraints to be properly evaluated, they need to be embedded in the Ecore metamodel or registered with EMF. The current implementation validates:

1. **Structural constraints** from the Ecore metamodel (cardinalities, types, etc.)
2. **EMF-embedded OCL constraints** (if present in the Ecore file)

To fully integrate OCL constraints, you would need to either:
- Embed the OCL constraints in the Ecore file using annotations
- Use Eclipse OCL's Complete OCL feature
- Generate Java validation code from the OCL constraints

If you need full OCL constraint evaluation, consider using Eclipse IDE with the OCL plugin, or extending this validator to parse and evaluate OCL constraints programmatically.
