import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional
import uuid

class FigmaXMLConverter:
    def __init__(self):
        self.ns = {
            'xmi': "http://www.omg.org/XMI",
            'xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'figma_meta_model': "www.figma_meta_model.com"
        }
        
    def convert_to_figma_xml(self, json_data: Dict[str, Any], name: str = "Untitled") -> str:
        """Convert JSON data to Figma XML format"""
        # Create root element
        root = ET.Element("figma_meta_model:FigmaApp")
        
        # Add namespaces and attributes
        root.set("xmi:version", "2.0")
        for prefix, uri in self.ns.items():
            root.set(f"xmlns:{prefix}", uri)
        root.set("xsi:schemaLocation", "www.figma_meta_model.com ../Metamodel/figma_meta_model.ecore")
        root.set("name", name)
        
        # Create document
        document = ET.SubElement(root, "document")
        document.set("id", "0:0")
        document.set("name", "Document")
        
        # Create canvas
        canvas = ET.SubElement(document, "children")
        canvas.set("xsi:type", "figma_meta_model:Canvas")
        canvas.set("type", "CANVAS")
        canvas.set("name", "JSON Content")
        canvas.set("id", f"{uuid.uuid4()}")
        
        # Create main frame
        main_frame = ET.SubElement(canvas, "children")
        main_frame.set("xsi:type", "figma_meta_model:Frame")
        main_frame.set("type", "FRAME")
        main_frame.set("name", "JSON Data")
        main_frame.set("id", f"{uuid.uuid4()}")
        
        # Process JSON content
        self._process_json_node(main_frame, json_data)
        
        # Convert to string with proper formatting
        return self._prettify_xml(root)
    
    def _process_json_node(self, parent: ET.Element, data: Any, name: str = "item") -> None:
        """Process a JSON node and create corresponding XML elements"""
        if isinstance(data, dict):
            component_set = ET.SubElement(parent, "children")
            component_set.set("xsi:type", "figma_meta_model:COMPONENT_SET")
            component_set.set("type", "COMPONENT_SET")
            component_set.set("name", name)
            
            component = ET.SubElement(component_set, "children")
            component.set("xsi:type", "figma_meta_model:Component")
            component.set("type", "COMPONENT")
            component.set("name", "Property 1=Default")
            
            frame = ET.SubElement(component, "children")
            frame.set("xsi:type", "figma_meta_model:Frame")
            frame.set("type", "FRAME")
            frame.set("name", "Frame")
            
            for key, value in data.items():
                self._process_json_node(frame, value, key)
                
        elif isinstance(data, list):
            frame = ET.SubElement(parent, "children")
            frame.set("xsi:type", "figma_meta_model:Frame")
            frame.set("type", "FRAME")
            frame.set("name", f"{name} List")
            
            for i, item in enumerate(data):
                self._process_json_node(frame, item, f"{name}_{i}")
                
        else:
            text = ET.SubElement(parent, "children")
            text.set("xsi:type", "figma_meta_model:Text")
            text.set("type", "TEXT")
            text.set("name", name)
            text.set("id", f"{uuid.uuid4()}")
            text.set("characters", str(data))
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Convert XML element to properly formatted string"""
        # Create XML declaration
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        
        # Convert element to string with proper indentation
        def _indent(elem: ET.Element, level: int = 0) -> None:
            i = "\n" + level * "  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for subelem in elem:
                    _indent(subelem, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        
        _indent(elem)
        return xml_declaration + ET.tostring(elem, encoding='unicode')

# Example usage
if __name__ == "__main__":
    # Sample JSON data
    json_data = {
        "input": {
            "label": "Username",
            "placeholder": "Enter username",
            "helper_text": "Must be at least 3 characters"
        },
        "button": {
            "text": "Submit",
            "type": "primary"
        }
    }
    
    converter = FigmaXMLConverter()
    xml_output = converter.convert_to_figma_xml(json_data, "Login Form")
    print(xml_output)