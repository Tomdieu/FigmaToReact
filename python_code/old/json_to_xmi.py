#!/usr/bin/env python
"""
Example usage for the Figma to React code generator
This demonstrates the entire process:
1. Parsing the Figma JSON to XMI
2. Converting the XMI to React model using ATL
3. Generating React code from the React model
"""

import os
import json
from some2 import FigmaToXMIParser

def main():
    # 1. Define file paths
    figma_json_path = "response.json"
    xmi_output_path = "figma_model.xmi"
    
    print("=== Figma to React Code Generator ===")
    
    # 2. Create parser instance
    parser = FigmaToXMIParser()
    
    # 3. Load Figma JSON from file
    print(f"Loading Figma JSON from: {figma_json_path}")
    with open(figma_json_path, 'r', encoding='utf-8') as file:
        figma_json = json.load(file)
    
    # 4. Parse and generate XMI
    print(f"Parsing Figma JSON and generating XMI: {xmi_output_path}")
    parser.parse_figma_json(figma_json, xmi_output_path)
    
    print("\nProcess completed!")

if __name__ == "__main__":
    main()