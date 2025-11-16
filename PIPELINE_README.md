# Figma to React - Model-Driven Engineering Transformation Pipeline

## Overview

This project implements a complete Model-Driven Engineering (MDE) pipeline for transforming Figma designs into functional React applications. The pipeline consists of model validation, model-to-model transformation, and model-to-text code generation using ATL (Atlas Transformation Language).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FIGMA TO REACT - MDE PIPELINE                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Figma Design    │────▶│  Python Fetch    │────▶│  Figma XMI       │
│  (Figma API)     │     │  & Convert       │     │  Model           │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                  │                         │
                                  ▼                         ▼
                         ┌──────────────────┐     ┌──────────────────┐
                         │  main.py         │     │ OCL Validation   │
                         │  json_to_xmi.py  │     │ (45 rules)      │
                         └──────────────────┘     └──────────────────┘
                                                            │
                                                            ▼
┌──────────────────┐                             ┌──────────────────┐
│  React Model     │◀────────────────────────────│ Model-to-Model   │
│  (XMI)           │                             │ Transformation   │
└──────────────────┘                             └──────────────────┘
         │                                                │
         ▼                                                ▼
┌──────────────────┐                             ┌──────────────────┐
│ OCL Validation   │                             │ tranform.atl     │
│ (optional)       │                             │ - 2000+ LOC      │
└──────────────────┘                             │ - Layout Rules   │
                                                  └──────────────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  React.js Code   │◀────│  Model-to-Text   │
│  (JSX, Vite)     │     │  Transformation  │
└──────────────────┘     └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  refine2.atl     │
                         │  - Code Gen      │
                         │  - File Output   │
                         └──────────────────┘
```

## Pipeline Components

### 0. Figma Design Fetching (Python)

#### Python Scripts (`python_code/`)
**Purpose**: Fetch Figma designs from the Figma API and convert them to XMI format.

**Scripts**:
- **`main.py`** - Main entry point that:
  - Fetches Figma file from API using file key and token
  - Saves JSON response to `Model/figma_instance.json`
  - Converts JSON to XMI format using custom parser
  - Pretty-prints the XMI for readability

- **`json_to_xmi.py`** - XMI parser that:
  - Parses Figma JSON structure
  - Maps to Figma metamodel elements
  - Generates valid XMI conforming to `figma_meta_model.ecore`

**Dependencies**:
- `requests` - HTTP library for Figma API calls
- `python-dotenv` - Environment variable management

**Configuration**:
- `.env` file with `FIGMA_TOKEN` (get from Figma account settings)
- File key in `main.py` (from Figma file URL)

**Output**:
- `Model/figma_instance.json` - Raw Figma API response
- `Model/figma_instance.xmi` - XMI model instance

### 1. Metamodels

#### Figma Metamodel (`Metamodel/figma_meta_model.ecore`)
Defines the structure of Figma designs including:
- **Document Structure**: FigmaApp, Document, Canvas, Pages
- **Node Types**: Frame, Component, Instance, Text, Rectangle, etc.
- **Layout Properties**: Auto-layout, constraints, spacing, padding
- **Styling**: Colors, effects, strokes, fills
- **Components**: Component definitions, instances, variants, properties
- **Interactions**: Navigation, prototyping flows

#### React Metamodel (`Metamodel/react_meta_model.ecore`)
Defines the structure of React applications including:
- **Application**: ReactApplication, Router, Routes
- **Pages**: Page components with routing
- **Components**: Reusable React components
- **JSX Elements**: HTMLElement, Component instances
- **Attributes**: Props, styles, event handlers

### 2. Transformations

#### Model-to-Model Transformation (`Transformations/tranform.atl`)
- **Source**: Figma instance model (figma_instance.xmi)
- **Target**: React instance model (react_new_instance.xmi)
- **Rules**: ~2000+ lines of ATL code
- **Key Mappings**:
  - Figma Frames → React Components/Divs
  - Figma Text → React Text Elements
  - Figma Components → React Components
  - Figma Auto-layout → CSS Flexbox
  - Figma Styles → Inline React styles

#### Model-to-Text Transformation (`Transformations/refine2.atl`)
- **Source**: React instance model (react_new_instance.xmi)
- **Target**: React.js application source code
- **Output Directory**: `./<AppName>/` (named after your Figma design)
- **Generates**:
  - `package.json` - Dependencies and scripts
  - `vite.config.js` - Build configuration
  - `index.html` - HTML entry point
  - `src/main.jsx` - React entry point
  - `src/App.jsx` - Main app with routing
  - `src/pages/*.jsx` - Page components
  - `src/components/*.jsx` - Reusable components

**Note**: The generated React application is created in a folder named after your Figma design. For example, if your Figma file is named "Untitled", the React app will be in `./Untitled/`.

### 3. Validation

#### OCL Constraints (`Metamodel/figma_meta_model.ocl`)
Enforces model integrity with 50+ constraints:
- **Basic Validation**: Non-empty names, unique IDs
- **Color Constraints**: RGBA values in [0.0, 1.0]
- **Dimension Constraints**: Positive width/height
- **Layout Constraints**: Valid layout modes, non-negative spacing
- **Text Constraints**: Non-empty text, valid font properties
- **Component Constraints**: Valid component references
- **Business Logic**: No circular references, consistent sizing

## Installation & Prerequisites

### Required Software

1. **Python 3.7+** (for Figma API fetching)
   ```bash
   python3 --version
   ```

2. **Java 11+** (for ATL execution and OCL validation)
   ```bash
   java -version
   ```

3. **Eclipse IDE** with ATL plugins
   - Eclipse Modeling Tools
   - ATL (Atlas Transformation Language)
   - EMF (Eclipse Modeling Framework)
   - OCL (Object Constraint Language)

4. **Maven** (for building OCL validator)
   ```bash
   mvn -version
   ```

5. **Node.js & npm** (for running generated React apps)
   ```bash
   node -version
   npm -version
   ```

### Setup

1. **Configure Figma API Access**

   Create a `.env` file in the `python_code/` directory:
   ```bash
   cp python_code/.env.example python_code/.env
   nano python_code/.env
   ```

   Add your Figma API token:
   ```
   FIGMA_TOKEN=your_figma_personal_access_token_here
   ```

   Get your token from: https://www.figma.com/developers/api#access-tokens

2. **Install Python Dependencies**

   ```bash
   cd python_code
   pip3 install -r requirements.txt
   cd ..
   ```

   Or use a virtual environment:
   ```bash
   cd python_code
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

3. **Configure Eclipse Path**

   Edit the `ECLIPSE_HOME` variable in the transformation scripts:
   ```bash
   ECLIPSE_HOME="/path/to/your/eclipse"
   ```

   Files to update:
   - `transform_figma_to_react.sh`
   - `refine_react.sh`

4. **Build OCL Validator**
   ```bash
   cd ocl-validator
   ./build.sh
   cd ..
   ```

5. **Make Scripts Executable**
   ```bash
   chmod +x *.sh
   chmod +x ocl-validator/*.sh
   ```

## Usage

### Option 1: Complete Pipeline (Recommended)

Run the entire pipeline with one command:

```bash
./run_complete_pipeline.sh
```

This executes:
1. ✓ Fetch Figma design from API and convert to XMI
2. ✓ OCL validation of Figma model
3. ✓ Model-to-model transformation (Figma → React)
4. ✓ Model-to-text transformation (React model → React code)
5. ✓ Summary report with generated artifacts

**Pipeline Configuration:**

You can control which steps to run using environment variables:

```bash
# Skip Figma fetch (use existing figma_instance.xmi)
FETCH_FIGMA=false ./run_complete_pipeline.sh

# Run only transformation and refinement (skip fetch and validation)
FETCH_FIGMA=false VALIDATE_FIGMA=false ./run_complete_pipeline.sh

# Run only model-to-model transformation
RUN_REFINEMENT=false ./run_complete_pipeline.sh

# Custom configuration
FETCH_FIGMA=true VALIDATE_FIGMA=true RUN_TRANSFORMATION=true RUN_REFINEMENT=false ./run_complete_pipeline.sh
```

### Option 2: Individual Steps

#### Step 1: Fetch Figma Design

```bash
cd python_code
python3 main.py
cd ..
```

Fetches design from Figma API and converts to XMI:
- **Input**: Figma file key (in main.py) + FIGMA_TOKEN (.env)
- **Output**: `Model/figma_instance.json`, `Model/figma_instance.xmi`

#### Step 2: Validate Figma Model

```bash
./validate_models.sh figma
```

Validates `Model/figma_instance.xmi` against OCL constraints.

#### Step 3: Model-to-Model Transformation

```bash
./transform_figma_to_react.sh
```

Transforms:
- **Input**: `Model/figma_instance.xmi`
- **Output**: `Model/react_new_instance.xmi`
- **ATL**: `Transformations/tranform.atl`

#### Step 4: Validate React Model (Optional)

```bash
./validate_models.sh react
```

Validates `Model/react_new_instance.xmi` (requires OCL constraints).

#### Step 5: Model-to-Text Transformation

```bash
./refine_react.sh
```

Generates:
- **Input**: `Model/react_new_instance.xmi`
- **Output**: Complete React.js application
- **ATL**: `Transformations/refine2.atl`

### Option 3: Validate All Models

```bash
./validate_models.sh all
```

Validates both Figma and React models.

## Running the Generated Application

After the pipeline completes, a React application will be generated in a folder named after your Figma design.

**Finding Your Generated App:**

The output folder name comes from the `name` attribute in your Figma file:
- Figma file named "MyApp" → generates `./MyApp/`
- Figma file named "Untitled" → generates `./Untitled/`
- Figma file named "Dashboard" → generates `./Dashboard/`

**Running the App:**

```bash
# Navigate to generated project (use your Figma design name)
cd <YourAppName>

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Example:**
```bash
# If your Figma design is named "Untitled"
cd Untitled
npm install
npm run dev
# Open browser to http://localhost:5173
```

The generated app includes:
- ✓ React 18 with modern hooks
- ✓ React Router for navigation
- ✓ Vite for fast development
- ✓ Component-based architecture
- ✓ Responsive layouts from Figma auto-layout

## Project Structure

```
FigmaToReact/
├── Metamodel/
│   ├── figma_meta_model.ecore       # Figma metamodel
│   ├── figma_meta_model.ocl         # Figma OCL constraints (50+ rules)
│   └── react_meta_model.ecore       # React metamodel
├── Model/
│   ├── figma_instance.xmi           # Figma design instance (input)
│   ├── figma_instance.json          # Original Figma JSON
│   └── react_new_instance.xmi       # React model (M2M output)
├── Transformations/
│   ├── tranform.atl                 # M2M transformation (2000+ LOC)
│   └── refine2.atl                  # M2T transformation (600+ LOC)
├── ocl-validator/
│   ├── src/                         # Java OCL validator
│   ├── pom.xml                      # Maven configuration
│   ├── build.sh                     # Build validator
│   └── validate.sh                  # Run validation
├── run_complete_pipeline.sh         # ⭐ Master pipeline script
├── transform_figma_to_react.sh      # M2M transformation
├── refine_react.sh                  # M2T transformation
├── validate_models.sh               # Model validation
└── PIPELINE_README.md               # This file
```

## Transformation Details

### Model-to-Model Transformation Rules

The `tranform.atl` file includes sophisticated transformation rules:

1. **Application Structure**
   - `FigmaApp2ReactApplication`: Creates React app with routing
   - `Document2Router`: Maps Figma pages to React routes

2. **Component Recognition**
   - `Component2Component`: Figma components → React components
   - `Instance2ComponentInstance`: Component instances with props
   - `ComponentSet2Component`: Component variants

3. **Layout Transformation**
   - `Frame2Element`: Smart frame mapping (div/nav/header/footer/section)
   - Auto-layout → CSS Flexbox (row/column direction)
   - Constraint-based sizing (fill, hug, fixed)
   - Spacing and padding preservation

4. **UI Element Mapping**
   - `Text2Text`: Text elements with styling
   - `Button2Button`: Interactive button components
   - `Image2Img`: Image elements
   - `Icon2SVG`: Icon to SVG conversion

5. **Style Transformation**
   - Color conversion (Figma 0-1 → CSS 0-255 RGBA)
   - Typography (font family, size, weight, line height)
   - Effects (shadows, blurs)
   - Borders and corner radius

### Model-to-Text Code Generation

The `refine2.atl` query generates a complete React application:

1. **Project Configuration**
   - `package.json` with dependencies
   - `vite.config.js` with PWA support
   - `index.html` entry point

2. **React Application**
   - `main.jsx` - React entry point
   - `App.jsx` - Router configuration with nested routes
   - Page components with proper imports
   - Reusable component library

3. **Code Quality**
   - Proper JSX formatting
   - Component naming conventions (PascalCase)
   - Props documentation
   - Clean separation of concerns

## Validation & Quality Assurance

### OCL Constraints Categories

1. **Structural Integrity** (15 rules)
   - Valid names and IDs
   - Unique identifiers
   - Proper parent-child relationships

2. **Data Validation** (12 rules)
   - Color values in valid range
   - Positive dimensions
   - Valid font properties

3. **Layout Consistency** (10 rules)
   - Valid layout modes
   - Non-negative spacing/padding
   - Consistent sizing constraints

4. **Business Logic** (8 rules)
   - No circular component references
   - Valid component property types
   - Consistent auto-resize settings

5. **Interaction Validation** (5 rules)
   - Valid navigation targets
   - Positive transition durations

## Troubleshooting

### Common Issues

#### 1. ATL Transformation Fails

**Problem**: "Eclipse launcher not found" or "ATL engine not found"

**Solution**:
- Verify `ECLIPSE_HOME` path in scripts
- Install ATL plugins in Eclipse
- Check Eclipse Modeling Tools installation

#### 2. OCL Validation Fails

**Problem**: "Validator JAR not found"

**Solution**:
```bash
cd ocl-validator
./build.sh
cd ..
```

#### 3. Generated Code Has Errors

**Problem**: React components have syntax errors

**Solution**:
- Check model-to-model transformation output
- Validate react_new_instance.xmi structure
- Review refine2.atl for code generation issues

#### 4. Permission Denied

**Problem**: Cannot execute shell scripts

**Solution**:
```bash
chmod +x *.sh
chmod +x ocl-validator/*.sh
```

### Debug Mode

Enable verbose output for debugging:

```bash
# In transform_figma_to_react.sh or refine_react.sh
# Add -consoleLog flag to see detailed Eclipse output
java -jar "$ECLIPSE_LAUNCHER" ... -consoleLog 2>&1 | tee transformation.log
```

## Research Context

This pipeline is part of a master's research project on Model-Driven Engineering for UI development. The research explores:

- **Automated UI Code Generation**: Transforming design artifacts into production code
- **Model Consistency**: Using OCL to ensure model integrity
- **Transformation Patterns**: Identifying reusable transformation rules
- **Code Quality**: Generating maintainable, idiomatic React code

### Key Contributions

1. **Comprehensive Metamodels**: Detailed Figma and React metamodels covering real-world scenarios
2. **Complex Transformations**: 2000+ lines of ATL rules handling layout, styling, and component hierarchies
3. **Validation Framework**: 45 OCL constraints ensuring model quality
4. **End-to-End Automation**: Complete pipeline from design to deployable application


## Future Work

- [ ] Add OCL constraints for React metamodel
- [ ] Support for Figma variants and component properties
- [ ] Animation and interaction code generation
- [ ] TypeScript code generation option
- [ ] Testing code generation (Jest, React Testing Library)
- [ ] Storybook integration for components
- [ ] Accessibility (a11y) checks and ARIA attributes

## License

[MIT]

## Contact

- **Author**: Ivan Tom
- **Email**: ivan.tomdieu@gmail.com
- **Research Project**: https://github.com/Tomdieu/FigmaToReact

## Acknowledgments

- ATL (Atlas Transformation Language) team
- Eclipse Modeling Framework (EMF) community
- Figma API documentation

---

**Last Updated**: November 2025
**Pipeline Version**: 1.0.0
