import json
from typing import List, Dict, Any

class FigmaXMLConverter:
    def __init__(self):
        self.xml: List[str] = []
        self.indent: int = 0
    
    def add_line(self, line: str) -> None:
        """Add a line to the XML output with proper indentation."""
        self.xml.append(" " * self.indent + line)
    
    def convert_to_xml(self, figma_json: Dict[str, Any]) -> str:
        """Convert Figma JSON to XML/XMI format."""
        # Start with XML declaration and root element
        self.add_line('<?xml version="1.0" encoding="UTF-8"?>')
        self.add_line('<figma_meta_model:FigmaApp')
        self.indent += 2
        self.add_line('xmi:version="2.0"')
        self.add_line('xmlns:xmi="http://www.omg.org/XMI"')
        self.add_line('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        self.add_line('xmlns:figma_meta_model="www.figma_meta_model.com"')
        self.add_line('xsi:schemaLocation="www.figma_meta_model.com ../Metamodel/figma_meta_model.ecore"')
        self.add_line(f'name="{figma_json["name"]}">')

        # Process document
        self.process_document(figma_json["document"])

        # Close root element
        self.indent -= 2
        self.add_line('</figma_meta_model:FigmaApp>')

        return "\n".join(self.xml)

    def process_document(self, document: Dict[str, Any]) -> None:
        """Process the document node."""
        self.indent += 2
        self.add_line('<document')
        self.add_line(f'id="{document["id"]}"')
        self.add_line(f'name="{document["name"]}">')

        # Process children
        if "children" in document:
            for child in document["children"]:
                self.process_node(child)

        self.add_line('</document>')
        self.indent -= 2

    def process_node(self, node: Dict[str, Any]) -> None:
        """Process a node in the Figma document."""
        self.indent += 2

        # Start node
        node_type = self.get_node_type(node)
        self.add_line('<children')
        self.add_line(f'xsi:type="figma_meta_model:{node_type}"')
        self.add_line(f'type="{node["type"]}"')
        self.add_line(f'name="{node["name"]}"')
        
        if "id" in node:
            self.add_line(f'id="{node["id"]}"')
        
        if "characters" in node:
            self.add_line(f'characters="{node["characters"]}"')

        if "children" not in node or not node["children"]:
            self.add_line('/>')
        else:
            self.add_line('>')
            
            # Process child nodes
            for child in node["children"]:
                self.process_node(child)

            # Process interactions if they exist
            if "interactions" in node and node["interactions"]:
                self.process_interactions(node["interactions"])

            self.add_line('</children>')

        self.indent -= 2

    def process_interactions(self, interactions: List[Dict[str, Any]]) -> None:
        """Process interaction nodes."""
        self.indent += 2
        self.add_line('<interactions>')
        
        for interaction in interactions:
            if "trigger" in interaction:
                self.add_line('<trigger')
                self.add_line(f'type="{interaction["trigger"]["type"]}"/>')
            
            if "actions" in interaction:
                for action in interaction["actions"]:
                    self.add_line('<actions')
                    if "destinationId" in action:
                        self.add_line(f'destinationId="{action["destinationId"]}"')
                    if "navigation" in action:
                        self.add_line(f'navigation="{action["navigation"]}"/>')
        
        self.add_line('</interactions>')
        self.indent -= 2

    @staticmethod
    def get_node_type(node: Dict[str, Any]) -> str:
        """Map Figma node types to XML types."""
        type_mapping = {
            'CANVAS': 'CANVAS',
            'FRAME': 'FRAME',
            'COMPONENT_SET': 'COMPONENT_SET',
            'COMPONENT': 'COMPONENT',
            'TEXT': 'TEXT'
        }
        return type_mapping.get(node["type"], node["type"])
