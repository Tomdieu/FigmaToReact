import requests
from figma_xml_converter import FigmaXMLConverter
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_figma_file(file_key: str, figma_token: str):
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {
        "X-Figma-Token": figma_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Example usage
file_key = "HDmpqjXyKIlTDxSIr9Vq4M"
figma_token = os.getenv("FIGMA_TOKEN")
figma_data = get_figma_file(file_key, figma_token)

# Convert to XML and save to a file
converter = FigmaXMLConverter()
xml_output = converter.convert_to_xml(figma_data)

with open('figma_instance.xmi', 'w') as file:
    file.write(xml_output)
