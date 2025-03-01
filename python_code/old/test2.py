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
            'figma_meta_model': 'www.figma_meta_model.com'
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
        
        # Track which attributes have been set on each element to avoid duplicates
        self.element_attributes = {}

    def set_attribute_safely(self, element, attribute_name, value):
        """
        Safely set an attribute on an element, converting None to empty string
        and ensuring no duplicate attributes
        
        Args:
            element: XML element to set attribute on
            attribute_name: Name of the attribute
            value: Value to set (may be None)
        """
        # Generate a unique ID for the element if not already done
        element_id = id(element)
        if element_id not in self.element_attributes:
            self.element_attributes[element_id] = set()
            
        # Check if this attribute has already been set on this element
        if attribute_name in self.element_attributes[element_id]:
            # Skip setting the attribute again to avoid duplicates
            return
            
        # Add this attribute to the tracking set
        self.element_attributes[element_id].add(attribute_name)
        
        # Convert None to empty string, otherwise use string representation
        if value is None:
            element.set(attribute_name, "")
        else:
            # if isinstance(value, bool):
            #     element.set(attribute_name, value)
            # elif isinstance(value,int):
            #     element.set(attribute_name, value)
            # elif isinstance(value,float):
            #     element.set(value,value)
            # else:
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
        # Reset attribute tracking for a new parsing session
        self.element_attributes = {}
        
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        # Clean None values to prevent serialization errors
        data = self.clean_none_values(data)
            
        # Create root element
        figma_app = ET.Element('figma_meta_model:FigmaApp')
        
        # Add namespace attributes
        # self.set_attribute_safely(figma_app, f'xmlns:xmi', self.nsmap['xmi'])
        # self.set_attribute_safely(figma_app, f'xmlns:xsi', self.nsmap['xsi'])
        self.set_attribute_safely(figma_app, f'xmlns:figma_meta_model', self.nsmap['figma_meta_model'])
        self.set_attribute_safely(figma_app,f'xsi:schemaLocation','www.figma_meta_model.com ../Metamodel/figma_meta_model.ecore')
        # self.set_attribute_safely(figma_app, f'{{{self.nsmap["xsi"]}}}schemaLocation', 'www.figma_meta_model.com ../Metamodel/figma_meta_model.ecore')
        
        # Create FigmaApp element
        # figma_app = ET.SubElement(xmi_root, 'figma_meta_model:FigmaApp')
        # self.set_attribute_safely(figma_app, f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        # Add basic app metadata
        if 'name' in data:
            self.set_attribute_safely(figma_app, 'name', data.get('name'))
        if 'lastModified' in data:
            self.set_attribute_safely(figma_app, 'lastModified', data.get('lastModified'))
        if 'thumbnailUrl' in data:
            self.set_attribute_safely(figma_app, 'thumbnailUrl', data.get('thumbnailUrl'))
        if 'version' in data:
            self.set_attribute_safely(figma_app, 'version', data.get('version'))
            
        self.set_attribute_safely(figma_app, 'editorType', 'figma')
        
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
        tree = ET.ElementTree(figma_app)
        
        # Save directly without using minidom for pretty printing
        # This avoids the duplicate attribute issue
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        print(f"XMI file generated successfully at: {output_path}")

    def process_document(self, document: Dict, parent_element: ET.Element) -> None:
        """
        Process the document element
        
        Args:
            document: Document JSON object
            parent_element: Parent XML element
        """
        document_elem = ET.SubElement(parent_element, 'document')
        # document_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
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
        child_elem = ET.SubElement(parent_element, 'children')
        #child_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        child_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:{child_type}')
        
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
                
        dimensions_elem = ET.SubElement(parent_element, dimension_type)
        
        # Set dimension attributes directly without type
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
                
        constraints_elem = ET.SubElement(parent_element, 'constraints')
        
        # Set attributes directly without type
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
                
        style_elem = ET.SubElement(parent_element, 'style')
        
        # Set style attributes directly on the style element without type attribute
        style_attributes = [
            'fontFamily', 'fontPostScriptName', 'textAutoResize', 'fontSize', 
            'fontWeight', 'letterSpacing', 'lineHeightPercent', 'lineHeightPx',
            'textAlignHorizontal', 'textAlignVertical'
        ]
        
        for attr in style_attributes:
            if attr in style:
                if attr == "lineHeightUnit":
                    continue
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
                if attr == "itemSpacing":
                    value = int(frame_data.get(attr))
                else:
                    value = frame_data.get(attr)
                self.set_attribute_safely(frame_element, attr, value)
                
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
                
        color_elem = ET.SubElement(parent_element, color_type)
        
        # Set color attributes directly without type attribute
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
            
        grid_elem = ET.SubElement(parent_element, 'layoutGrids')
        #grid_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        grid_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:LayoutGrid')
        
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
            
        weights_elem = ET.SubElement(parent_element, 'individualStrokeWeights')
        # weights_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        weights_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:StrokeWeight')
        
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
                dash_elem = ET.SubElement(comp_set_element, 'strokeDashes')
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
        
        # Process each definition
        for key, value in definitions.items():
            # Create componentPropertyDefinitions element with key attribute
            def_container = ET.SubElement(parent_element, 'componentPropertyDefinitions')
            self.set_attribute_safely(def_container, 'key', key)
            
            # Create componentpropertydefinition element with definition attributes
            def_data = ET.SubElement(def_container, 'componentpropertydefinition')
            
            if 'type' in value:
                self.set_attribute_safely(def_data, 'type', value.get('type'))
            
            if 'defaultValue' in value:
                self.set_attribute_safely(def_data, 'defaultValue', value.get('defaultValue'))
                
            # Process variant options if they exist
            if 'variantOptions' in value and isinstance(value['variantOptions'], list):
                for option in value['variantOptions']:
                    option_elem = ET.SubElement(def_data, 'variantOptions')
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
            
        override_elem = ET.SubElement(parent_element, 'overrides')
        # override_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        override_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Override')
        
        if 'id' in override:
            self.set_attribute_safely(override_elem, 'id', override.get('id'))
            
        if 'overriddenFields' in override and isinstance(override['overriddenFields'], list):
            for field in override['overriddenFields']:
                field_elem = ET.SubElement(override_elem, 'overriddenFields')
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
            prop_data = ET.SubElement(parent_element, 'componentProperties')
            self.set_attribute_safely(prop_data, 'key', key)
            
            # Create the value element (not ComponentProperty)
            if value is not None:
                value_elem = ET.SubElement(prop_data, 'value')
                
                if 'type' in value:
                    self.set_attribute_safely(value_elem, 'type', value.get('type'))
                    
                if 'value' in value:
                    self.set_attribute_safely(value_elem, 'value', value.get('value'))


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
            
        device_elem = ET.SubElement(parent_element, 'prototypeDevice')
        # device_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        device_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:PrototypeDevice')
        
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
            
        point_elem = ET.SubElement(parent_element, 'flowStartingPoints')
        # point_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        point_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:FlowStartingPoint')
        
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
                
        # Create a container element with the proper name (fills, background, strokes)
        bg_container = ET.SubElement(parent_element, background_type)
        
        for bg in backgrounds:
            if bg is None:
                continue
            
            # Process color directly without creating a Background element
            if 'color' in bg and bg['color'] is not None:
                color_elem = ET.SubElement(bg_container, 'color')
                
                # Set color attributes directly
                for key in ['r', 'g', 'b', 'a']:
                    if key in bg['color']:
                        self.set_attribute_safely(color_elem, key, bg['color'].get(key))

    def process_effect(self, effect: Dict, parent_element: ET.Element) -> None:
        """
        Process effect information
        
        Args:
            effect: Effect JSON object
            parent_element: Parent XML element
        """
        if effect is None:
            return
            
        effect_elem = ET.SubElement(parent_element, 'effects')
        # effect_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        # effect_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Effect')
        
        effect_attributes = ['radius', 'visible', 'type']
        
        for attr in effect_attributes:
            if attr in effect:
                self.set_attribute_safely(effect_elem, attr, effect.get(attr))
                
        if 'blendMode' in effect:
            self.set_attribute_safely(effect_elem, 'blenMode', effect.get('blendMode'))

    def process_interaction(self, interaction: Dict, parent_element: ET.Element) -> None:
        """
        Process interaction information
        
        Args:
            interaction: Interaction JSON object
            parent_element: Parent XML element
        """
        if interaction is None:
            return
            
        interaction_elem = ET.SubElement(parent_element, 'interactions')
        # interaction_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        interaction_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Interaction')
        
        # Process trigger
        if 'trigger' in interaction:
            self.process_trigger(interaction['trigger'], interaction_elem)
            
        # Process actions
        if 'actions' in interaction and isinstance(interaction['actions'], list):
            for action in interaction['actions']:
                self.process_action(action, interaction_elem)

    def process_trigger(self, trigger: Dict, parent_element: ET.Element) -> None:
        """
        Process trigger information
        
        Args:
            trigger: Trigger JSON object
            parent_element: Parent XML element
        """
        if trigger is None:
            return
            
        trigger_elem = ET.SubElement(parent_element, 'trigger')
        # trigger_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        trigger_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Trigger')
        
        if 'type' in trigger:
            self.set_attribute_safely(trigger_elem, 'type', trigger.get('type'))

    def process_action(self, action: Dict, parent_element: ET.Element) -> None:
        """
        Process action information
        
        Args:
            action: Action JSON object
            parent_element: Parent XML element
        """
        # Skip null actions
        if action is None:
            return
            
        action_elem = ET.SubElement(parent_element, 'actions')
        # action_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        action_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Action')
        
        action_attributes = ['type', 'destinationId', 'navigation']
        
        for attr in action_attributes:
            if attr in action and action[attr] is not None:
                self.set_attribute_safely(action_elem, attr, action.get(attr))
                
        # Process transition
        if 'transition' in action and action['transition'] is not None:
            self.process_transition(action['transition'], action_elem)

    def process_transition(self, transition: Dict, parent_element: ET.Element) -> None:
        """
        Process transition information
        
        Args:
            transition: Transition JSON object
            parent_element: Parent XML element
        """
        if transition is None:
            return
            
        transition_elem = ET.SubElement(parent_element, 'transition')
        # transition_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        transition_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Transition')
        
        transition_attributes = ['type', 'direction', 'duration', 'matchLayers']
        
        for attr in transition_attributes:
            if attr in transition:
                self.set_attribute_safely(transition_elem, attr, transition.get(attr))
                
        # Process easing
        if 'easing' in transition:
            self.process_easing(transition['easing'], transition_elem)
            
    def process_easing(self, easing: Dict, parent_element: ET.Element) -> None:
        """
        Process easing information
        
        Args:
            easing: Easing JSON object
            parent_element: Parent XML element
        """
        if easing is None:
            return
            
        easing_elem = ET.SubElement(parent_element, 'easing')
        # easing_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        easing_elem.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:Easing')
        
        if 'type' in easing:
            self.set_attribute_safely(easing_elem, 'type', easing.get('type'))
            
    def process_component_property_reference(self, key: str, value: str, parent_element: ET.Element) -> None:
        """
        Process component property reference
        
        Args:
            key: Reference key
            value: Reference value
            parent_element: Parent XML element
        """
        if key is None or value is None:
            return
                
        ref_elem = ET.SubElement(parent_element, 'componentPropertyReferences')
        
        # Set attributes directly on the componentPropertyReferences element
        self.set_attribute_safely(ref_elem, 'key', key)
        self.set_attribute_safely(ref_elem, 'value', value)
        
    def process_components(self, components: Dict, parent_element: ET.Element) -> None:
        """
        Process components
        
        Args:
            components: Components JSON object
            parent_element: Parent XML element
        """
        if components is None:
            return
                
        for comp_id, comp_data in components.items():
            # Create components element with id attribute
            comp_container = ET.SubElement(parent_element, 'components')
            self.set_attribute_safely(comp_container, 'id', comp_id)
            
            # Create data element with component attributes directly
            data_elem = ET.SubElement(comp_container, 'data')
            
            # Set component attributes directly on the data element
            if comp_data:
                if 'key' in comp_data:
                    self.set_attribute_safely(data_elem, 'key', comp_data.get('key'))
                
                if 'name' in comp_data:
                    self.set_attribute_safely(data_elem, 'name', comp_data.get('name'))
                    
                if 'description' in comp_data:
                    self.set_attribute_safely(data_elem, 'description', comp_data.get('description'))
                    
                if 'remote' in comp_data:
                    self.set_attribute_safely(data_elem, 'remote', str(comp_data.get('remote')).lower())
                    
                if 'componentSetId' in comp_data:
                    self.set_attribute_safely(data_elem, 'componentSetId', comp_data.get('componentSetId'))
            
            
    def process_component_sets(self, component_sets: Dict, parent_element: ET.Element) -> None:
        """
        Process component sets
        
        Args:
            component_sets: Component sets JSON object
            parent_element: Parent XML element
        """
        if component_sets is None:
            return
                
        for set_id, set_data in component_sets.items():
            # Create componentSets element with id attribute
            set_container = ET.SubElement(parent_element, 'componentSets')
            self.set_attribute_safely(set_container, 'id', set_id)
            
            # Create data element with component set attributes directly
            data_elem = ET.SubElement(set_container, 'data')
            
            # Set component set attributes directly on the data element
            if set_data:
                if 'key' in set_data:
                    self.set_attribute_safely(data_elem, 'key', set_data.get('key'))
                
                if 'name' in set_data:
                    self.set_attribute_safely(data_elem, 'name', set_data.get('name'))
                    
                if 'description' in set_data:
                    self.set_attribute_safely(data_elem, 'description', set_data.get('description'))
                    
                if 'componentSetId' in set_data:
                    self.set_attribute_safely(data_elem, 'componentSetId', set_data.get('componentSetId'))
            
    def process_component_item(self, comp_data: Dict, parent_element: ET.Element) -> None:
        """
        Process component item
        
        Args:
            comp_data: Component data JSON object
            parent_element: Parent XML element
        """
        if comp_data is None:
            return
            
        comp_item = ET.SubElement(parent_element, 'ComponentItem')
        # comp_item.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        # comp_item.set(f'{{{self.nsmap["xsi"]}}}type', f'figma_meta_model:ComponentItem')
        
        # Process component attributes
        comp_attributes = ['key', 'name', 'description', 'remote', 'componentSetId']
        
        for attr in comp_attributes:
            if attr in comp_data:
                self.set_attribute_safely(comp_item, attr, comp_data.get(attr))
                
        # Process documentation links
        if 'documentationLinks' in comp_data and isinstance(comp_data['documentationLinks'], list):
            for link in comp_data['documentationLinks']:
                link_elem = ET.SubElement(comp_item, 'documentationLinks')
                # If link is a string, use it directly, otherwise convert to string
                if link is not None:
                    if isinstance(link, str):
                        link_elem.text = link
                    else:
                        link_elem.text = str(link)
                else:
                    link_elem.text = ""

# Alternative version with more formatting options
def pretty_print_xmi_advanced(input_file: str, output_file: str):
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        # First parse with ElementTree for structure
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Convert to string with minidom for pretty printing
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        
        # Advanced formatting
        pretty_xml = dom.toprettyxml(
            indent="    ",
            newl='\n',
            encoding='UTF-8'
        )
        
        # Clean up formatting
        lines = []
        for line in pretty_xml.decode('utf-8').split('\n'):
            if line.strip():  # Remove empty lines
                # Remove extra whitespace but preserve structure
                if '>' in line and '<' in line:
                    line = line.rstrip()
                lines.append(line)
        
        formatted_xml = '\n'.join(lines)
        
        # Write formatted output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_xml)
            
        print(f"Advanced formatted XMI saved to: {output_file}")
        
    except Exception as e:
        print(f"Error in advanced formatting: {e}")

def main():
    """
    Main entry point for the script when executed directly
    """
    import argparse
    from xml.dom import minidom
    
    parser = argparse.ArgumentParser(description="Convert Figma JSON to XMI format")
    parser.add_argument("input_file", help="Path to the Figma JSON file")
    parser.add_argument("output_file", help="Path for the output XMI file")
    args = parser.parse_args()
    
    # Create parser instance
    figma_parser = FigmaToXMIParser()
    
    # Read input JSON
    with open(args.input_file, 'r', encoding='utf-8') as file:
        figma_json = json.load(file)

    # Parse and generate XMI
    figma_parser.parse_figma_json(figma_json, args.output_file)

    def pretty_print_xmi(input_file: str, output_file: str, indent: str = "  "):
        try:
            # Parse the input XMI file into a DOM
            dom = minidom.parse(input_file)
            # Generate a pretty-printed XML string
            pretty_xml = dom.toprettyxml(indent=indent)
            
            # Write the pretty-printed XML to the output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            
            print(f"Pretty-printed XMI has been saved to: {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")

    pretty_print_xmi(args.output_file, "pretify_instance.xmi")
    
if __name__ == "__main__":
    main()