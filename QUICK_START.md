# Quick Start Guide - Figma to React Pipeline

## TL;DR - Run the Complete Pipeline

```bash
# Execute the entire transformation pipeline
./run_complete_pipeline.sh
```

This single command will:
1. ✓ Fetch Figma design from API and convert to XMI
2. ✓ Validate your Figma model using OCL constraints
3. ✓ Transform Figma model to React model (M2M)
4. ✓ Generate React.js application code (M2T)
5. ✓ Display summary report

---

## Available Commands

### 🚀 Master Pipeline (Recommended)

```bash
./run_complete_pipeline.sh
```

**Configuration Options:**
```bash
# Skip Figma fetch (use existing figma_instance.xmi)
FETCH_FIGMA=false ./run_complete_pipeline.sh

# Skip validation (not recommended for production)
VALIDATE_FIGMA=false ./run_complete_pipeline.sh

# Bypass strict validation (debugging only)
STRICT_VALIDATION=false ./run_complete_pipeline.sh

# Only M2M transformation
FETCH_FIGMA=false RUN_REFINEMENT=false ./run_complete_pipeline.sh

# Only M2T transformation (requires react_new_instance.xmi)
FETCH_FIGMA=false RUN_TRANSFORMATION=false ./run_complete_pipeline.sh
```

**🔒 Validation Enforcement (Default):**

By default, the pipeline **STOPS** if OCL validation fails:
- ✅ Valid model → Proceeds to transformation
- ❌ Invalid model → Pipeline STOPS (protects quality)

See `VALIDATION_ENFORCEMENT.md` for details.

---

### 🎨 Fetch Figma Design

```bash
cd python_code
python3 main.py
cd ..
```

**Fetches and converts:**
- **Input**: Figma API (file key + token)
- **Output**: `Model/figma_instance.json` + `Model/figma_instance.xmi`

**Requirements:**
- Python 3.7+
- `requests` and `python-dotenv` packages
- `.env` file with `FIGMA_TOKEN`
- Figma file key in `main.py`

---

### 🔍 Model Validation

```bash
# Validate Figma model (default)
./validate_models.sh

# Validate specific model
./validate_models.sh figma
./validate_models.sh react

# Validate all models
./validate_models.sh all
```

**Validates against:**
- 50+ OCL constraints
- Structural integrity
- Data consistency
- Business logic rules

---

### 🔄 Model-to-Model Transformation

```bash
./transform_figma_to_react.sh
```

**Transformation:**
- **Input**: `Model/figma_instance.xmi`
- **Output**: `Model/react_new_instance.xmi`
- **Rules**: `Transformations/tranform.atl` (2000+ lines)

**What it does:**
- Figma Frames → React Components/Divs
- Figma Components → React Components
- Figma Auto-layout → CSS Flexbox
- Figma Styles → Inline React Styles
- Component instances with props

---

### 📝 Model-to-Text Transformation

```bash
./refine_react.sh
```

**Code Generation:**
- **Input**: `Model/react_new_instance.xmi`
- **Output**: Complete React.js application
- **Query**: `Transformations/refine2.atl` (600+ lines)

**Generates:**
- `package.json` - Dependencies
- `vite.config.js` - Build config
- `index.html` - Entry point
- `src/main.jsx` - React entry
- `src/App.jsx` - Router
- `src/pages/*.jsx` - Page components
- `src/components/*.jsx` - Reusable components

---

## Running Generated Application

The React app is generated in a folder named after your Figma design.

```bash
# Navigate to generated app (use your Figma design name)
cd <YourFigmaDesignName>

# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Example:** If your Figma file is named "Untitled":
```bash
cd Untitled
npm install
npm run dev
```

**How to find your app name:**
- Check the pipeline output for "Detected application name"
- Or look at the folder created in the project root
- The name matches your Figma file name

---

## File Structure

```
FigmaToReact/
├── run_complete_pipeline.sh    ⭐ Run this for complete pipeline
├── validate_models.sh           🔍 Model validation
├── transform_figma_to_react.sh  🔄 M2M transformation
├── refine_react.sh              📝 M2T code generation
│
├── Metamodel/
│   ├── figma_meta_model.ecore   # Source metamodel
│   ├── figma_meta_model.ocl     # OCL constraints (50+ rules)
│   └── react_meta_model.ecore   # Target metamodel
│
├── Model/
│   ├── figma_instance.xmi       # Input: Figma design
│   └── react_new_instance.xmi   # Output: React model
│
├── Transformations/
│   ├── tranform.atl             # M2M rules (2000+ LOC)
│   └── refine2.atl              # M2T query (600+ LOC)
│
└── ocl-validator/
    ├── build.sh                 # Build validator
    └── validate.sh              # Run validation
```

---

## Prerequisites Check

### 1. Python
```bash
python3 --version
# Required: Python 3.7+

# Install dependencies
cd python_code
pip3 install -r requirements.txt
cd ..

# Configure Figma API token
cp python_code/.env.example python_code/.env
# Edit .env and add your FIGMA_TOKEN
```

### 2. Java
```bash
java -version
# Required: Java 11+
```

### 3. Eclipse with ATL
```bash
# Update ECLIPSE_HOME in scripts:
# - transform_figma_to_react.sh
# - refine_react.sh
```

### 4. Maven
```bash
mvn -version
# Required for building OCL validator
```

### 5. Node.js
```bash
node -version
npm -version
# Required for running generated apps
```

---

## First Time Setup

```bash
# 1. Setup Python environment and Figma API
cd python_code
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # Add your FIGMA_TOKEN
cd ..

# 2. Build OCL validator
cd ocl-validator
./build.sh
cd ..

# 3. Verify scripts are executable
ls -lh *.sh
# Should show -rwxrwxr-x permissions

# 4. Update Eclipse path if needed
nano transform_figma_to_react.sh
# Change ECLIPSE_HOME="/home/ivantom/tool/eclipse"

# 5. Update Figma file key if needed
nano python_code/main.py
# Change file_key = "your_figma_file_key"

# 6. Run the complete pipeline
./run_complete_pipeline.sh
```

---

## Workflow Examples

### Example 1: Full Pipeline for Research Paper

```bash
# Complete transformation with validation
./run_complete_pipeline.sh > pipeline_output.log 2>&1

# Check results
cat pipeline_output.log
ls -lh Model/figma_instance.xmi Model/react_new_instance.xmi

# Find generated app (will be named after your Figma design)
ls -d */ | grep -v -E 'Model|Metamodel|Transformations|python_code|ocl-validator|atl-runner|images|workspace'

# Run the generated app
cd <YourAppName>  # Use the name from the Figma design
npm install && npm run dev
```

### Example 2: Iterative Development

```bash
# Step 1: Fetch Figma design
cd python_code && python3 main.py && cd ..

# Step 2: Validate source model
./validate_models.sh figma

# Step 3: Run transformation only
FETCH_FIGMA=false VALIDATE_FIGMA=false RUN_REFINEMENT=false ./run_complete_pipeline.sh

# Step 4: Inspect intermediate model
# (Use Eclipse to view Model/react_new_instance.xmi)

# Step 5: Generate code
FETCH_FIGMA=false RUN_TRANSFORMATION=false ./run_complete_pipeline.sh
```

### Example 3: Debugging Transformations

```bash
# Skip fetch if XMI exists
FETCH_FIGMA=false ./run_complete_pipeline.sh

# Or run steps individually:
# 1. Fetch
cd python_code && python3 main.py && cd ..

# 2. Transform M2M
./transform_figma_to_react.sh

# 3. Manually check react_new_instance.xmi in Eclipse

# 4. Generate code M2T
./refine_react.sh
```

---

## Troubleshooting

### Error: "FIGMA_TOKEN not found"
```bash
# Create .env file
cp python_code/.env.example python_code/.env
nano python_code/.env
# Add: FIGMA_TOKEN=your_token_here
```

### Error: "Python module not found"
```bash
cd python_code
pip3 install -r requirements.txt
cd ..
```

### Error: "Failed to fetch Figma design"
```bash
# Check:
# 1. FIGMA_TOKEN is valid (get from figma.com/settings)
# 2. File key is correct in main.py
# 3. Internet connection works
```

### Error: "Eclipse launcher not found"
```bash
# Update ECLIPSE_HOME in scripts
export ECLIPSE_HOME="/path/to/your/eclipse"
```

### Error: "Validator JAR not found"
```bash
cd ocl-validator
./build.sh
cd ..
```

### Error: "Permission denied"
```bash
chmod +x *.sh
chmod +x ocl-validator/*.sh
```

### Error: "ATL engine not found"
```bash
# Install ATL in Eclipse:
# Help > Eclipse Marketplace > Search "ATL" > Install
```

---

## Output Examples

### Successful Pipeline Execution

```
================================================================================
           FIGMA TO REACT - COMPLETE TRANSFORMATION PIPELINE
================================================================================
Pipeline Configuration:
  Fetch Figma Design: true
  Validate Figma Model: true
  Run M2M Transformation: true
  Validate React Model: false
  Run M2T Refinement: true
================================================================================

[STEP 1] Fetching Figma Design from API
────────────────────────────────────────────────────────────────────────────
✓ Figma design fetched and converted to XMI
  Output: Model/figma_instance.xmi (234567 bytes)
  JSON: Model/figma_instance.json

[STEP 2] Validating Figma Instance Model
────────────────────────────────────────────────────────────────────────────
✓ Figma model validation PASSED

[STEP 3] Model-to-Model Transformation (Figma → React)
────────────────────────────────────────────────────────────────────────────
✓ Model-to-Model transformation COMPLETED
  Output size: 45678 bytes

[STEP 4] Model-to-Text Transformation (React Model → React Code)
────────────────────────────────────────────────────────────────────────────
✓ Model-to-Text transformation COMPLETED
Generated React application at: ./MyApp

================================================================================
                        PIPELINE EXECUTION SUMMARY
================================================================================
✓ Pipeline completed successfully!
Total execution time: 28 seconds

Generated Artifacts:
  ✓ Model/figma_instance.xmi
  ✓ Model/react_new_instance.xmi

Pipeline Steps Executed:
  ✓ Fetch Figma Design (API → XMI)
  ✓ Figma Model Validation (OCL)
  ✓ Model-to-Model Transformation
  ✓ Model-to-Text Transformation
================================================================================
```

---

## Key Metrics for Research

After running the pipeline, collect these metrics:

### Transformation Metrics
```bash
# Line count of transformation rules
wc -l Transformations/tranform.atl
wc -l Transformations/refine2.atl

# Model size
ls -lh Model/figma_instance.xmi
ls -lh Model/react_new_instance.xmi

# Generated code size
cd <AppName>
find src -name "*.jsx" | xargs wc -l
```

### Validation Metrics
```bash
# Number of OCL constraints
grep -c "^inv" Metamodel/figma_meta_model.ocl

# Validation execution time
time ./validate_models.sh figma
```

### Code Generation Metrics
```bash
# Number of generated files
find <AppName>/src -type f | wc -l

# Component count
find <AppName>/src/components -name "*.jsx" | wc -l

# Page count
find <AppName>/src/pages -name "*.jsx" | wc -l
```

---

## For Your Master's Thesis

### Commands for Demonstration

```bash
# 1. Show pipeline execution
./run_complete_pipeline.sh

# 2. Show validation details
./validate_models.sh figma

# 3. Show generated application
cd <AppName>
npm install
npm run dev
# Open browser to http://localhost:5173
```

### Pipeline Screenshots

Capture these for your thesis:
1. Pipeline execution output
2. OCL validation results
3. Generated file structure
4. Running React application
5. Component hierarchy in browser DevTools

### Research Artifacts

Include these in your thesis appendix:
- `PIPELINE_README.md` - Complete documentation
- `Transformations/tranform.atl` - Transformation rules
- `Transformations/refine2.atl` - Code generation
- `Metamodel/figma_meta_model.ocl` - OCL constraints
- Generated React application code samples

---

## Next Steps

1. ✓ Run the complete pipeline
2. ✓ Verify generated application works
3. ✓ Document transformation patterns
4. ✓ Measure code quality metrics
5. ✓ Compare with manual React development
6. ✓ Write thesis sections

---

## Support

For issues or questions:
1. Check `PIPELINE_README.md` for detailed documentation
2. Review transformation logs
3. Validate input models
4. Check Eclipse ATL installation

---

**Quick Reference Card**

| Task | Command |
|------|---------|
| Run everything | `./run_complete_pipeline.sh` |
| Fetch Figma | `cd python_code && python3 main.py && cd ..` |
| Validate only | `./validate_models.sh figma` |
| Transform only | `./transform_figma_to_react.sh` |
| Generate code | `./refine_react.sh` |
| Build validator | `cd ocl-validator && ./build.sh` |
| Run app | `cd <YourFigmaDesignName> && npm install && npm run dev` |
| Skip fetch | `FETCH_FIGMA=false ./run_complete_pipeline.sh` |
| Find app folder | `ls -d */ \| grep -v Model \| grep -v Metamodel` |

---

**Last Updated**: November 2025
