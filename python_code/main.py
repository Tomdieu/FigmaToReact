import logging
from json_to_xmi import FigmaToXMIParser
import json
import requests
from dotenv import load_dotenv
import os
from xml.dom import minidom
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def get_figma_file(file_key: str, figma_token: str) -> dict:
    """
    Retrieve Figma file JSON data using the provided file key and token.
    """
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": figma_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def pretty_print_xmi(input_file: str, output_file: str, indent: str = "  ") -> None:
    """
    Pretty-print the XMI by parsing the XML file and saving the formatted content.
    """
    try:
        # Parse the input XMI file into a DOM
        dom = minidom.parse(input_file)
        pretty_xml = dom.toprettyxml(indent=indent)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        logger.info("Pretty-printed XMI has been saved to: %s", output_file)
    except Exception as e:
        logger.exception("Error processing file: %s", e)


def main() -> None:
    """
    Main entry point for the script when executed directly.
    """
    parser = argparse.ArgumentParser(description="Convert Figma JSON to XMI.")
    parser.add_argument("--file_key", type=str, help="Figma file key to retrieve.")
    args = parser.parse_args()

    # Default file key if none is provided
    file_key = args.file_key if args.file_key else "HDmpqjXyKIlTDxSIr9Vq4M"
    logger.info(f"Using Figma file_key: {file_key}")
    print(f"Using Figma file_key: {file_key}")
    

    figma_token = os.getenv("FIGMA_TOKEN")
    if not figma_token:
        raise ValueError("FIGMA_TOKEN not found in environment variables.")

    figma_parser = FigmaToXMIParser()
    figma_json = get_figma_file(file_key, figma_token)
    print("Figma JSON file retrieved successfully.")

    # Save JSON
    with open('../Model/figma_instance.json', 'w', encoding='utf-8') as f:
        json.dump(figma_json, f, ensure_ascii=False, indent=4)
    print("Figma JSON file saved to ../Model/figma_instance.json")

    # Output XMI path
    output_file = '../Model/figma_instance.xmi'

    # Generate XMI
    figma_parser.parse_figma_json(figma_json, output_file)
    print(f"XMI has been generated and saved to: {output_file}")

    # Pretty-print XMI
    pretty_print_xmi(output_file, output_file)
    print(f"Pretty-printed XMI has been saved to: {output_file}")

if __name__ == "__main__":
    main()


# def main() -> None:
#     """
#     Main entry point for the script when executed directly.
#     """
#     figma_parser = FigmaToXMIParser()
#     file_key = "HDmpqjXyKIlTDxSIr9Vq4M"
#     figma_token = os.getenv("FIGMA_TOKEN")
#     figma_json = get_figma_file(file_key, figma_token)
#     # create json file
#     with open('../Model/figma_instance.json', 'w', encoding='utf-8') as f:
#         json.dump(figma_json, f, ensure_ascii=False, indent=4)
#     # Specify the output file path
#     output_file = '../Model/figma_instance.xmi'
#     # Parse and generate XMI
#     figma_parser.parse_figma_json(figma_json, output_file)
#     # Pretty-print the generated XMI
#     pretty_print_xmi(output_file, output_file)

# if __name__ == "__main__":
#     main()
