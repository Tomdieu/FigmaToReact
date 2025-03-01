import json
import uuid
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union

class FigmaToXMIParser:
    """
    Parser to convert Figma JSON to XMI format according to the figma_meta_model.ecore
    """
    def __init__(self):
        # Namespace definitions
        self.nsmap = {
            'xmi': 'http://www.omg.org/XMI',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'figmaMM': 'www.figma_meta_model.com'
        }
        
        # Register namespaces for proper rendering
        for prefix, uri in self.nsmap.items():
            ET.register_namespace(prefix, uri)
            
        # Create document type mappings
        self.document_type_map = {
            'DOCUMENT': 'DOCUMENT',
            'CANVAS': 'CANVAS',
            'RECTANGLE': 'RECTANGLE',
            'FRAME': 'FRAME',
            'TEXT': 'TEXT',
            'COMPONENT': 'COMPONENT',
            'COMPONENT_SET': 'COMPONENT_SET',
            'VECTOR': 'VECTOR',
            'LINE': 'LINE',
            'INSTANCE': 'INSTANCE',
            'GROUP': 'FRAME'  # Mapping GROUP to FRAME as they're similar
        }
        
        # Initialize ID tracking for references
        self.id_map = {}

    def set_attribute_safely(self, element, attribute_name, value):
        """
        Safely set an attribute on an element, converting None to empty string
        
        Args:
            element: XML element to set attribute on
            attribute_name: Name of the attribute
            value: Value to set (may be None)
        """
        # Convert None to empty string, otherwise use string representation
        if value is None:
            element.set(attribute_name, "")
        else:
            element.set(attribute_name, str(value))

    def clean_none_values(self, data_dict):
        """Convert None values to empty strings in a nested dictionary"""
        if isinstance(data_dict, dict):
            for key, value in list(data_dict.items()):
                if value is None:
                    data_dict[key] = ""
                elif isinstance(value, (dict, list)):
                    self.clean_none_values(value)
        elif isinstance(data_dict, list):
            for item in data_dict:
                if isinstance(item, (dict, list)):
                    self.clean_none_values(item)
        return data_dict

    def parse_figma_json(self, json_data: Union[str, Dict], output_path: str) -> None:
        """
        Main method to parse Figma JSON and generate XMI file
        
        Args:
            json_data: Figma JSON data as string or dictionary
            output_path: Path where to save the XMI file
        """
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        # Clean None values to prevent serialization errors
        data = self.clean_none_values(data)
            
        # Create root element
        xmi_root = ET.Element(f'{{{self.nsmap["xmi"]}}}XMI')
        
        # Add namespace attributes
        xmi_root.set(f'xmlns:xmi', self.nsmap['xmi'])
        xmi_root.set(f'xmlns:xsi', self.nsmap['xsi'])
        xmi_root.set(f'xmlns:figmaMM', self.nsmap['figmaMM'])
        xmi_root.set(f'{{{self.nsmap["xsi"]}}}schemaLocation', 'www.figma_meta_model.com figma_meta_model.ecore')
        
        # Create FigmaApp element
        figma_app = ET.SubElement(xmi_root, '{%s}FigmaApp' % self.nsmap['figmaMM'])
        figma_app.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        # Add basic app metadata
        if 'name' in data:
            self.set_attribute_safely(figma_app, 'name', data.get('name'))
        if 'lastModified' in data:
            self.set_attribute_safely(figma_app, 'lastModified', data.get('lastModified'))
        if 'thumbnailUrl' in data:
            self.set_attribute_safely(figma_app, 'thumbnailUrl', data.get('thumbnailUrl'))
        if 'version' in data:
            self.set_attribute_safely(figma_app, 'version', data.get('version'))
            
        figma_app.set('editorType', 'figma')
        
        # Process document
        if 'document' in data:
            self.process_document(data['document'], figma_app)
            
        # Process components
        if 'components' in data:
            self.process_components(data['components'], figma_app)
            
        # Process component sets
        if 'componentSets' in data:
            self.process_component_sets(data['componentSets'], figma_app)
            
        # Write the tree to file with pretty formatting
        tree = ET.ElementTree(xmi_root)
        rough_string = ET.tostring(xmi_root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
            
        print(f"XMI file generated successfully at: {output_path}")

    def process_document(self, document: Dict, parent_element: ET.Element) -> None:
        """
        Process the document element
        
        Args:
            document: Document JSON object
            parent_element: Parent XML element
        """
        document_elem = ET.SubElement(parent_element, '{%s}Document' % self.nsmap['figmaMM'])
        document_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        # Set basic document attributes
        if 'id' in document:
            self.set_attribute_safely(document_elem, 'id', document.get('id'))
            self.id_map[document['id']] = document_elem
            
        if 'name' in document:
            self.set_attribute_safely(document_elem, 'name', document.get('name'))
            
        document_elem.set('type', 'DOCUMENT')
        
        if 'scrollBehavior' in document:
            self.set_attribute_safely(document_elem, 'scrollBehavior', document.get('scrollBehavior'))
            
        # Process children
        if 'children' in document and isinstance(document['children'], list):
            for child in document['children']:
                self.process_child(child, document_elem)

    def process_child(self, child: Dict, parent_element: ET.Element) -> None:
        """
        Process a child element based on its type
        
        Args:
            child: Child JSON object
            parent_element: Parent XML element
        """
        child_type = child.get('type', None)
        if not child_type or child_type not in self.document_type_map:
            print(f"Warning: Unknown child type: {child_type}")
            return
        
        # Map the type to our model's type
        element_type = self.document_type_map[child_type]
        
        # Create the appropriate element
        child_elem = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], element_type))
        child_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        # Set basic attributes
        if 'id' in child:
            self.set_attribute_safely(child_elem, 'id', child.get('id'))
            self.id_map[child['id']] = child_elem
            
        if 'name' in child:
            self.set_attribute_safely(child_elem, 'name', child.get('name'))
            
        self.set_attribute_safely(child_elem, 'type', child_type)
        
        # Set scrollBehavior
        if 'scrollBehavior' in child:
            self.set_attribute_safely(child_elem, 'scrollBehavior', child.get('scrollBehavior'))
        else:
            child_elem.set('scrollBehavior', 'SCROLLS')
            
        # Process clipsContent
        if 'clipsContent' in child:
            self.set_attribute_safely(child_elem, 'clipsContent', str(child.get('clipsContent')).lower())
        else:
            child_elem.set('clipsContent', 'false')
            
        # Process stroke information
        if 'strokeWeight' in child:
            self.set_attribute_safely(child_elem, 'strokeWeight', child.get('strokeWeight'))
            
        if 'strokeAlign' in child:
            self.set_attribute_safely(child_elem, 'strokeAlign', child.get('strokeAlign'))
        
        # Process absoluteBoundingBox
        if 'absoluteBoundingBox' in child:
            self.process_dimensions(child['absoluteBoundingBox'], child_elem, 'absoluteBoundingBox')
            
        # Process absoluteRenderBounds
        if 'absoluteRenderBounds' in child:
            self.process_dimensions(child['absoluteRenderBounds'], child_elem, 'absoluteRenderBounds')
            
        # Process constraints
        if 'constraints' in child:
            self.process_constraints(child['constraints'], child_elem)
        
        # Process specific attributes for TEXT type
        if element_type == 'TEXT':
            self.process_text_specific(child, child_elem)
        
        # Process specific attributes for FRAME type
        elif element_type == 'FRAME':
            self.process_frame_specific(child, child_elem)
        
        # Process specific attributes for COMPONENT_SET type
        elif element_type == 'COMPONENT_SET':
            self.process_component_set_specific(child, child_elem)
        
        # Process specific attributes for INSTANCE type
        elif element_type == 'INSTANCE':
            self.process_instance_specific(child, child_elem)
        
        # Process specific attributes for CANVAS type
        elif element_type == 'CANVAS':
            self.process_canvas_specific(child, child_elem)
            
        # Process fills
        if 'fills' in child and isinstance(child['fills'], list) and len(child['fills']) > 0:
            self.process_background(child['fills'], child_elem, 'fills')
            
        # Process background
        if 'background' in child and isinstance(child['background'], list) and len(child['background']) > 0:
            self.process_background(child['background'], child_elem, 'background')
            
        # Process strokes
        if 'strokes' in child and isinstance(child['strokes'], list) and len(child['strokes']) > 0:
            self.process_background(child['strokes'], child_elem, 'strokes')
            
        # Process effects
        if 'effects' in child and isinstance(child['effects'], list):
            for effect in child['effects']:
                self.process_effect(effect, child_elem)
                
        # Process interactions
        if 'interactions' in child and isinstance(child['interactions'], list):
            for interaction in child['interactions']:
                self.process_interaction(interaction, child_elem)
                
        # Process componentPropertyReferences
        if 'componentPropertyReferences' in child and isinstance(child['componentPropertyReferences'], dict):
            for key, value in child['componentPropertyReferences'].items():
                self.process_component_property_reference(key, value, child_elem)
        
        # Process children recursively
        if 'children' in child and isinstance(child['children'], list):
            for grandchild in child['children']:
                self.process_child(grandchild, child_elem)

    def process_dimensions(self, dimensions: Dict, parent_element: ET.Element, dimension_type: str) -> None:
        """
        Process dimension information
        
        Args:
            dimensions: Dimension JSON object
            parent_element: Parent XML element
            dimension_type: Type of dimension (absoluteBoundingBox or absoluteRenderBounds)
        """
        if dimensions is None:
            return
            
        dimensions_elem = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], dimension_type))
        dimensions_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key in ['x', 'y', 'width', 'height']:
            if key in dimensions:
                self.set_attribute_safely(dimensions_elem, key, dimensions.get(key))

    def process_constraints(self, constraints: Dict, parent_element: ET.Element) -> None:
        """
        Process constraints information
        
        Args:
            constraints: Constraints JSON object
            parent_element: Parent XML element
        """
        if constraints is None:
            return
            
        constraints_elem = ET.SubElement(parent_element, '{%s}constraints' % self.nsmap['figmaMM'])
        constraints_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'horizontal' in constraints:
            self.set_attribute_safely(constraints_elem, 'horizontal', constraints.get('horizontal'))
            
        if 'vertical' in constraints:
            self.set_attribute_safely(constraints_elem, 'vertical', constraints.get('vertical'))

    def process_text_specific(self, text_data: Dict, text_element: ET.Element) -> None:
        """
        Process TEXT specific attributes
        
        Args:
            text_data: TEXT JSON object
            text_element: TEXT XML element
        """
        if 'characters' in text_data:
            self.set_attribute_safely(text_element, 'characters', text_data.get('characters'))
            
        if 'style' in text_data:
            self.process_style(text_data['style'], text_element)
            
        if 'layoutAlign' in text_data:
            self.set_attribute_safely(text_element, 'layoutAlign', text_data.get('layoutAlign'))
            
        if 'layoutGrow' in text_data:
            self.set_attribute_safely(text_element, 'layoutGrow', text_data.get('layoutGrow'))
            
        if 'layoutSizingHorizontal' in text_data:
            self.set_attribute_safely(text_element, 'layoutSizingHorizontal', text_data.get('layoutSizingHorizontal'))
            
        if 'layoutSizingVertical' in text_data:
            self.set_attribute_safely(text_element, 'layoutSizingVertical', text_data.get('layoutSizingVertical'))
            
        # Process line types
        if 'lineTypes' in text_data and isinstance(text_data['lineTypes'], list):
            for line_type in text_data['lineTypes']:
                self.set_attribute_safely(text_element, 'lineTypes', line_type)
                
        # Process line indentations
        if 'lineIndentations' in text_data and isinstance(text_data['lineIndentations'], list):
            for indentation in text_data['lineIndentations']:
                self.set_attribute_safely(text_element, 'lineIndentations', str(indentation))

    def process_style(self, style: Dict, parent_element: ET.Element) -> None:
        """
        Process style information
        
        Args:
            style: Style JSON object
            parent_element: Parent XML element
        """
        if style is None:
            return
            
        style_elem = ET.SubElement(parent_element, '{%s}style' % self.nsmap['figmaMM'])
        style_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        # Set style attributes
        style_attributes = [
            'fontFamily', 'fontPostScriptName', 'textAutoResize', 'fontSize', 
            'fontWeight', 'letterSpacing', 'lineHeightPercent', 'lineHeightPx',
            'lineHeightUnit', 'textAlignHorizontal', 'textAlignVertical'
        ]
        
        for attr in style_attributes:
            if attr in style:
                self.set_attribute_safely(style_elem, attr, style.get(attr))

    def process_frame_specific(self, frame_data: Dict, frame_element: ET.Element) -> None:
        """
        Process FRAME specific attributes
        
        Args:
            frame_data: FRAME JSON object
            frame_element: FRAME XML element
        """
        frame_attributes = [
            'layoutMode', 'layoutWrap', 'layoutSizingHorizontal', 'layoutSizingVertical',
            'layoutAlign', 'layoutVersion', 'counterAxisSizingMode', 'itemSpacing',
            'primaryAxisSizingMode', 'counterAxisAlignItems', 'primaryAxisAlignItems',
            'cornerRadius', 'cornerSmoothing'
        ]
        
        for attr in frame_attributes:
            if attr in frame_data:
                self.set_attribute_safely(frame_element, attr, frame_data.get(attr))
                
        # Process backgroundColor
        if 'backgroundColor' in frame_data:
            self.process_color(frame_data['backgroundColor'], frame_element, 'backgroundColor')
            
        # Process layoutGrids
        if 'layoutGrids' in frame_data and isinstance(frame_data['layoutGrids'], list):
            for grid in frame_data['layoutGrids']:
                self.process_layout_grid(grid, frame_element)
                
        # Process individualStrokeWeights
        if 'individualStrokeWeights' in frame_data:
            self.process_stroke_weights(frame_data['individualStrokeWeights'], frame_element)

    def process_color(self, color: Dict, parent_element: ET.Element, color_type: str) -> None:
        """
        Process color information
        
        Args:
            color: Color JSON object
            parent_element: Parent XML element
            color_type: Type of color element
        """
        if color is None:
            return
            
        color_elem = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], color_type))
        color_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key in ['r', 'g', 'b', 'a']:
            if key in color:
                self.set_attribute_safely(color_elem, key, color.get(key))

    def process_layout_grid(self, grid: Dict, parent_element: ET.Element) -> None:
        """
        Process layout grid information
        
        Args:
            grid: LayoutGrid JSON object
            parent_element: Parent XML element
        """
        if grid is None:
            return
            
        grid_elem = ET.SubElement(parent_element, '{%s}layoutGrids' % self.nsmap['figmaMM'])
        grid_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        grid_attributes = [
            'sectionSize', 'visible', 'alignment', 'gutterSize', 'offset', 'count'
        ]
        
        for attr in grid_attributes:
            if attr in grid:
                self.set_attribute_safely(grid_elem, attr, grid.get(attr))
                
        # Process color
        if 'color' in grid:
            self.process_color(grid['color'], grid_elem, 'color')

    def process_stroke_weights(self, weights: Dict, parent_element: ET.Element) -> None:
        """
        Process stroke weights information
        
        Args:
            weights: StrokeWeight JSON object
            parent_element: Parent XML element
        """
        if weights is None:
            return
            
        weights_elem = ET.SubElement(parent_element, '{%s}individualStrokeWeights' % self.nsmap['figmaMM'])
        weights_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key in ['top', 'right', 'bottom', 'left']:
            if key in weights:
                self.set_attribute_safely(weights_elem, key, weights.get(key))

    def process_component_set_specific(self, comp_set_data: Dict, comp_set_element: ET.Element) -> None:
        """
        Process COMPONENT_SET specific attributes
        
        Args:
            comp_set_data: COMPONENT_SET JSON object
            comp_set_element: COMPONENT_SET XML element
        """
        comp_set_attributes = [
            'layoutVersion', 'itemSpacing', 'cornerRadius', 'cornerSmoothing'
        ]
        
        for attr in comp_set_attributes:
            if attr in comp_set_data:
                self.set_attribute_safely(comp_set_element, attr, comp_set_data.get(attr))
                
        # Process backgroundColor
        if 'backgroundColor' in comp_set_data:
            self.process_color(comp_set_data['backgroundColor'], comp_set_element, 'backgroundColor')
            
        # Process strokeDashes
        if 'strokeDashes' in comp_set_data and isinstance(comp_set_data['strokeDashes'], list):
            for dash in comp_set_data['strokeDashes']:
                dash_elem = ET.SubElement(comp_set_element, '{%s}strokeDashes' % self.nsmap['figmaMM'])
                if dash is not None:
                    dash_elem.text = str(dash)
                else:
                    dash_elem.text = ""
                
        # Process componentPropertyDefinitions
        if 'componentPropertyDefinitions' in comp_set_data:
            self.process_component_property_definitions(comp_set_data['componentPropertyDefinitions'], comp_set_element)

    def process_component_property_definitions(self, definitions: Dict, parent_element: ET.Element) -> None:
        """
        Process component property definitions
        
        Args:
            definitions: ComponentPropertyDefinitions JSON object
            parent_element: Parent XML element
        """
        if definitions is None:
            return
            
        def_container = ET.SubElement(parent_element, '{%s}componentPropertyDefinitions' % self.nsmap['figmaMM'])
        def_container.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key, value in definitions.items():
            def_data = ET.SubElement(def_container, '{%s}componentpropertydefinition' % self.nsmap['figmaMM'])
            self.set_attribute_safely(def_data, 'key', key)
            
            prop_def = ET.SubElement(def_data, '{%s}ComponentPropertyDefinition' % self.nsmap['figmaMM'])
            prop_def.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            if 'type' in value:
                self.set_attribute_safely(prop_def, 'type', value.get('type'))
            
            if 'defaultValue' in value:
                self.set_attribute_safely(prop_def, 'defaultValue', value.get('defaultValue'))
                
            if 'variantOptions' in value and isinstance(value['variantOptions'], list):
                for option in value['variantOptions']:
                    option_elem = ET.SubElement(prop_def, '{%s}variantOptions' % self.nsmap['figmaMM'])
                    if option is not None:
                        option_elem.text = str(option)
                    else:
                        option_elem.text = ""

    def process_instance_specific(self, instance_data: Dict, instance_element: ET.Element) -> None:
        """
        Process INSTANCE specific attributes
        
        Args:
            instance_data: INSTANCE JSON object
            instance_element: INSTANCE XML element
        """
        if 'componentId' in instance_data:
            self.set_attribute_safely(instance_element, 'componentId', instance_data.get('componentId'))
            
        # Process overrides
        if 'overrides' in instance_data and isinstance(instance_data['overrides'], list):
            for override in instance_data['overrides']:
                self.process_override(override, instance_element)
                
        # Process componentProperties
        if 'componentProperties' in instance_data:
            self.process_component_properties(instance_data['componentProperties'], instance_element)

    def process_override(self, override: Dict, parent_element: ET.Element) -> None:
        """
        Process override information
        
        Args:
            override: Override JSON object
            parent_element: Parent XML element
        """
        if override is None:
            return
            
        override_elem = ET.SubElement(parent_element, '{%s}overrides' % self.nsmap['figmaMM'])
        override_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'id' in override:
            self.set_attribute_safely(override_elem, 'id', override.get('id'))
            
        if 'overriddenFields' in override and isinstance(override['overriddenFields'], list):
            for field in override['overriddenFields']:
                field_elem = ET.SubElement(override_elem, '{%s}overriddenFields' % self.nsmap['figmaMM'])
                if field is not None:
                    field_elem.text = str(field)
                else:
                    field_elem.text = ""

    def process_component_properties(self, properties: Dict, parent_element: ET.Element) -> None:
        """
        Process component properties
        
        Args:
            properties: ComponentProperties JSON object
            parent_element: Parent XML element
        """
        if properties is None:
            return
            
        for key, value in properties.items():
            prop_data = ET.SubElement(parent_element, '{%s}componentProperties' % self.nsmap['figmaMM'])
            prop_data.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            self.set_attribute_safely(prop_data, 'key', key)
            
            prop = ET.SubElement(prop_data, '{%s}ComponentProperty' % self.nsmap['figmaMM'])
            prop.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            if value is not None:
                if 'type' in value:
                    self.set_attribute_safely(prop, 'type', value.get('type'))
                    
                if 'value' in value:
                    self.set_attribute_safely(prop, 'value', value.get('value'))

    def process_canvas_specific(self, canvas_data: Dict, canvas_element: ET.Element) -> None:
        """
        Process CANVAS specific attributes
        
        Args:
            canvas_data: CANVAS JSON object
            canvas_element: CANVAS XML element
        """
        if 'prototypeStartNodeID' in canvas_data:
            self.set_attribute_safely(canvas_element, 'prototypeStartNodeID', canvas_data.get('prototypeStartNodeID'))
            
        # Process prototypeDevice
        if 'prototypeDevice' in canvas_data:
            self.process_prototype_device(canvas_data['prototypeDevice'], canvas_element)

    def process_prototype_device(self, device: Dict, parent_element: ET.Element) -> None:
        """
        Process prototype device information
        
        Args:
            device: PrototypeDevice JSON object
            parent_element: Parent XML element
        """
        if device is None:
            return
            
        device_elem = ET.SubElement(parent_element, '{%s}prototypeDevice' % self.nsmap['figmaMM'])
        device_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'type' in device:
            self.set_attribute_safely(device_elem, 'type', device.get('type'))
            
        if 'rotation' in device:
            self.set_attribute_safely(device_elem, 'rotation', device.get('rotation'))
            
        # Process flowStartingPoints
        if 'flowStartingPoints' in device and isinstance(device['flowStartingPoints'], list):
            for point in device['flowStartingPoints']:
                self.process_flow_starting_point(point, device_elem)

    def process_flow_starting_point(self, point: Dict, parent_element: ET.Element) -> None:
        """
        Process flow starting point information
        
        Args:
            point: FlowStartingPoint JSON object
            parent_element: Parent XML element
        """
        if point is None:
            return
            
        point_elem = ET.SubElement(parent_element, '{%s}flowStartingPoints' % self.nsmap['figmaMM'])
        point_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'nodeId' in point:
            self.set_attribute_safely(point_elem, 'nodeId', point.get('nodeId'))
            
        if 'name' in point:
            self.set_attribute_safely(point_elem, 'name', point.get('name'))

    def process_background(self, backgrounds: List[Dict], parent_element: ET.Element, background_type: str) -> None:
        """
        Process background information
        
        Args:
            backgrounds: Background JSON array
            parent_element: Parent XML element
            background_type: Type of background (fills, background, strokes)
        """
        if backgrounds is None:
            return
            
        bg_container = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], background_type))
        bg_container.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for bg in backgrounds:
            if bg is None:
                continue
                
            bg_elem = ET.SubElement(bg_container, '{%s}Background' % self.nsmap['figmaMM'])
            bg_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            if 'blendMode' in bg:
                self.set_attribute_safely(bg_elem, 'blendMode', bg