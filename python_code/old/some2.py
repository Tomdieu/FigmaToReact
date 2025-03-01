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
            figma_app.set('name', data['name'])
        if 'lastModified' in data:
            figma_app.set('lastModified', data['lastModified'])
        if 'thumbnailUrl' in data:
            figma_app.set('thumbnailUrl', data['thumbnailUrl'])
        if 'version' in data:
            figma_app.set('version', data['version'])
            
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
            document_elem.set('id', document['id'])
            self.id_map[document['id']] = document_elem
            
        if 'name' in document:
            document_elem.set('name', document['name'])
            
        document_elem.set('type', 'DOCUMENT')
        
        if 'scrollBehavior' in document:
            document_elem.set('scrollBehavior', document['scrollBehavior'])
            
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
            child_elem.set('id', child['id'])
            self.id_map[child['id']] = child_elem
            
        if 'name' in child:
            child_elem.set('name', child['name'])
            
        child_elem.set('type', child_type)
        
        # Set scrollBehavior
        if 'scrollBehavior' in child:
            child_elem.set('scrollBehavior', child['scrollBehavior'])
        else:
            child_elem.set('scrollBehavior', 'SCROLLS')
            
        # Process clipsContent
        if 'clipsContent' in child:
            child_elem.set('clipsContent', str(child['clipsContent']).lower())
        else:
            child_elem.set('clipsContent', 'false')
            
        # Process stroke information
        if 'strokeWeight' in child:
            child_elem.set('strokeWeight', str(child['strokeWeight']))
            
        if 'strokeAlign' in child:
            child_elem.set('strokeAlign', child['strokeAlign'])
        
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
        dimensions_elem = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], dimension_type))
        dimensions_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key in ['x', 'y', 'width', 'height']:
            if dimensions!= None:
                if key in dimensions:
                    dimensions_elem.set(key, str(dimensions[key]))

    def process_constraints(self, constraints: Dict, parent_element: ET.Element) -> None:
        """
        Process constraints information
        
        Args:
            constraints: Constraints JSON object
            parent_element: Parent XML element
        """
        constraints_elem = ET.SubElement(parent_element, '{%s}constraints' % self.nsmap['figmaMM'])
        constraints_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'horizontal' in constraints:
            constraints_elem.set('horizontal', constraints['horizontal'])
            
        if 'vertical' in constraints:
            constraints_elem.set('vertical', constraints['vertical'])

    def process_text_specific(self, text_data: Dict, text_element: ET.Element) -> None:
        """
        Process TEXT specific attributes
        
        Args:
            text_data: TEXT JSON object
            text_element: TEXT XML element
        """
        if 'characters' in text_data:
            text_element.set('characters', text_data['characters'])
            
        if 'style' in text_data:
            self.process_style(text_data['style'], text_element)
            
        if 'layoutAlign' in text_data:
            text_element.set('layoutAlign', text_data['layoutAlign'])
            
        if 'layoutGrow' in text_data:
            text_element.set('layoutGrow', str(text_data['layoutGrow']))
            
        if 'layoutSizingHorizontal' in text_data:
            text_element.set('layoutSizingHorizontal', text_data['layoutSizingHorizontal'])
            
        if 'layoutSizingVertical' in text_data:
            text_element.set('layoutSizingVertical', text_data['layoutSizingVertical'])
            
        # Process line types
        if 'lineTypes' in text_data and isinstance(text_data['lineTypes'], list):
            for line_type in text_data['lineTypes']:
                text_element.set('lineTypes', line_type)
                
        # Process line indentations
        if 'lineIndentations' in text_data and isinstance(text_data['lineIndentations'], list):
            for indentation in text_data['lineIndentations']:
                text_element.set('lineIndentations', str(indentation))

    def process_style(self, style: Dict, parent_element: ET.Element) -> None:
        """
        Process style information
        
        Args:
            style: Style JSON object
            parent_element: Parent XML element
        """
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
                style_elem.set(attr, str(style[attr]))

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
                frame_element.set(attr, str(frame_data[attr]))
                
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
        color_elem = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], color_type))
        color_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key in ['r', 'g', 'b', 'a']:
            if key in color:
                color_elem.set(key, str(color[key]))

    def process_layout_grid(self, grid: Dict, parent_element: ET.Element) -> None:
        """
        Process layout grid information
        
        Args:
            grid: LayoutGrid JSON object
            parent_element: Parent XML element
        """
        grid_elem = ET.SubElement(parent_element, '{%s}layoutGrids' % self.nsmap['figmaMM'])
        grid_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        grid_attributes = [
            'sectionSize', 'visible', 'alignment', 'gutterSize', 'offset', 'count'
        ]
        
        for attr in grid_attributes:
            if attr in grid:
                grid_elem.set(attr, str(grid[attr]))
                
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
        weights_elem = ET.SubElement(parent_element, '{%s}individualStrokeWeights' % self.nsmap['figmaMM'])
        weights_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key in ['top', 'right', 'bottom', 'left']:
            if key in weights:
                weights_elem.set(key, str(weights[key]))

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
                comp_set_element.set(attr, str(comp_set_data[attr]))
                
        # Process backgroundColor
        if 'backgroundColor' in comp_set_data:
            self.process_color(comp_set_data['backgroundColor'], comp_set_element, 'backgroundColor')
            
        # Process strokeDashes
        if 'strokeDashes' in comp_set_data and isinstance(comp_set_data['strokeDashes'], list):
            for dash in comp_set_data['strokeDashes']:
                dash_elem = ET.SubElement(comp_set_element, '{%s}strokeDashes' % self.nsmap['figmaMM'])
                dash_elem.text = str(dash)
                
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
        def_container = ET.SubElement(parent_element, '{%s}componentPropertyDefinitions' % self.nsmap['figmaMM'])
        def_container.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for key, value in definitions.items():
            def_data = ET.SubElement(def_container, '{%s}componentpropertydefinition' % self.nsmap['figmaMM'])
            def_data.set('key', key)
            
            prop_def = ET.SubElement(def_data, '{%s}ComponentPropertyDefinition' % self.nsmap['figmaMM'])
            prop_def.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            if 'type' in value:
                prop_def.set('type', value['type'])
            
            if 'defaultValue' in value:
                prop_def.set('defaultValue', str(value['defaultValue']))
                
            if 'variantOptions' in value and isinstance(value['variantOptions'], list):
                for option in value['variantOptions']:
                    option_elem = ET.SubElement(prop_def, '{%s}variantOptions' % self.nsmap['figmaMM'])
                    option_elem.text = option

    def process_instance_specific(self, instance_data: Dict, instance_element: ET.Element) -> None:
        """
        Process INSTANCE specific attributes
        
        Args:
            instance_data: INSTANCE JSON object
            instance_element: INSTANCE XML element
        """
        if 'componentId' in instance_data:
            instance_element.set('componentId', instance_data['componentId'])
            
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
        override_elem = ET.SubElement(parent_element, '{%s}overrides' % self.nsmap['figmaMM'])
        override_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'id' in override:
            override_elem.set('id', override['id'])
            
        if 'overriddenFields' in override and isinstance(override['overriddenFields'], list):
            for field in override['overriddenFields']:
                field_elem = ET.SubElement(override_elem, '{%s}overriddenFields' % self.nsmap['figmaMM'])
                field_elem.text = field

    def process_component_properties(self, properties: Dict, parent_element: ET.Element) -> None:
        """
        Process component properties
        
        Args:
            properties: ComponentProperties JSON object
            parent_element: Parent XML element
        """
        for key, value in properties.items():
            prop_data = ET.SubElement(parent_element, '{%s}componentProperties' % self.nsmap['figmaMM'])
            prop_data.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            prop_data.set('key', key)
            
            prop = ET.SubElement(prop_data, '{%s}ComponentProperty' % self.nsmap['figmaMM'])
            prop.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            if 'type' in value:
                prop.set('type', value['type'])
                
            if 'value' in value:
                prop.set('value', str(value['value']))

    def process_canvas_specific(self, canvas_data: Dict, canvas_element: ET.Element) -> None:
        """
        Process CANVAS specific attributes
        
        Args:
            canvas_data: CANVAS JSON object
            canvas_element: CANVAS XML element
        """
        if 'prototypeStartNodeID' in canvas_data:
            canvas_element.set('prototypeStartNodeID', canvas_data['prototypeStartNodeID'])
            
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
        device_elem = ET.SubElement(parent_element, '{%s}prototypeDevice' % self.nsmap['figmaMM'])
        device_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'type' in device:
            device_elem.set('type', device['type'])
            
        if 'rotation' in device:
            device_elem.set('rotation', device['rotation'])
            
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
        point_elem = ET.SubElement(parent_element, '{%s}flowStartingPoints' % self.nsmap['figmaMM'])
        point_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'nodeId' in point:
            point_elem.set('nodeId', point['nodeId'])
            
        if 'name' in point:
            point_elem.set('name', point['name'])

    def process_background(self, backgrounds: List[Dict], parent_element: ET.Element, background_type: str) -> None:
        """
        Process background information
        
        Args:
            backgrounds: Background JSON array
            parent_element: Parent XML element
            background_type: Type of background (fills, background, strokes)
        """
        bg_container = ET.SubElement(parent_element, '{%s}%s' % (self.nsmap['figmaMM'], background_type))
        bg_container.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        for bg in backgrounds:
            bg_elem = ET.SubElement(bg_container, '{%s}Background' % self.nsmap['figmaMM'])
            bg_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            if 'blendMode' in bg:
                bg_elem.set('blendMode', bg['blendMode'])
                
            if 'opacity' in bg:
                bg_elem.set('opacity', str(bg['opacity']))
                
            if 'type' in bg:
                bg_elem.set('type', bg['type'])
                
            # Process color
            if 'color' in bg:
                self.process_color(bg['color'], bg_elem, 'color')

    def process_effect(self, effect: Dict, parent_element: ET.Element) -> None:
        """
        Process effect information
        
        Args:
            effect: Effect JSON object
            parent_element: Parent XML element
        """
        effect_elem = ET.SubElement(parent_element, '{%s}effects' % self.nsmap['figmaMM'])
        effect_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        effect_attributes = ['radius', 'visible', 'type']
        
        for attr in effect_attributes:
            if attr in effect:
                effect_elem.set(attr, str(effect[attr]))
                
        if 'blendMode' in effect:
            effect_elem.set('blenMode', effect['blendMode'])

    def process_interaction(self, interaction: Dict, parent_element: ET.Element) -> None:
        """
        Process interaction information
        
        Args:
            interaction: Interaction JSON object
            parent_element: Parent XML element
        """
        interaction_elem = ET.SubElement(parent_element, '{%s}interactions' % self.nsmap['figmaMM'])
        interaction_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
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
        trigger_elem = ET.SubElement(parent_element, '{%s}trigger' % self.nsmap['figmaMM'])
        trigger_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'type' in trigger:
            trigger_elem.set('type', trigger['type'])

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
            
        action_elem = ET.SubElement(parent_element, '{%s}actions' % self.nsmap['figmaMM'])
        action_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        action_attributes = ['type', 'destinationId', 'navigation']
        
        for attr in action_attributes:
            if attr in action and action[attr] is not None:
                action_elem.set(attr, str(action[attr]))
                
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
        transition_elem = ET.SubElement(parent_element, '{%s}transition' % self.nsmap['figmaMM'])
        transition_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        transition_attributes = ['type', 'direction', 'duration', 'matchLayers']
        
        for attr in transition_attributes:
            if attr in transition:
                transition_elem.set(attr, str(transition[attr]))
                
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
        easing_elem = ET.SubElement(parent_element, '{%s}easing' % self.nsmap['figmaMM'])
        easing_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        if 'type' in easing:
            easing_elem.set('type', easing['type'])
            
    def process_component_property_reference(self, key: str, value: str, parent_element: ET.Element) -> None:
        """
        Process component property reference
        
        Args:
            key: Reference key
            value: Reference value
            parent_element: Parent XML element
        """
        ref_elem = ET.SubElement(parent_element, '{%s}componentPropertyReferences' % self.nsmap['figmaMM'])
        ref_elem.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        ref_elem.set('key', key)
        ref_elem.set('value', value)
        
    def process_components(self, components: Dict, parent_element: ET.Element) -> None:
        """
        Process components
        
        Args:
            components: Components JSON object
            parent_element: Parent XML element
        """
        for comp_id, comp_data in components.items():
            comp_container = ET.SubElement(parent_element, '{%s}components' % self.nsmap['figmaMM'])
            comp_container.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            comp_container.set('id', comp_id)
            
            comp_item = ET.SubElement(comp_container, '{%s}data' % self.nsmap['figmaMM'])
            comp_item.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            # Process component item attributes
            self.process_component_item(comp_data, comp_item)
            
    def process_component_sets(self, component_sets: Dict, parent_element: ET.Element) -> None:
        """
        Process component sets
        
        Args:
            component_sets: Component sets JSON object
            parent_element: Parent XML element
        """
        for set_id, set_data in component_sets.items():
            set_container = ET.SubElement(parent_element, '{%s}componentSets' % self.nsmap['figmaMM'])
            set_container.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            set_container.set('id', set_id)
            
            set_item = ET.SubElement(set_container, '{%s}data' % self.nsmap['figmaMM'])
            set_item.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
            
            # Process component item attributes
            self.process_component_item(set_data, set_item)
            
    def process_component_item(self, comp_data: Dict, parent_element: ET.Element) -> None:
        """
        Process component item
        
        Args:
            comp_data: Component data JSON object
            parent_element: Parent XML element
        """
        comp_item = ET.SubElement(parent_element, '{%s}ComponentItem' % self.nsmap['figmaMM'])
        comp_item.set(f'{{{self.nsmap["xmi"]}}}id', f'_{str(uuid.uuid4())}')
        
        # Process component attributes
        comp_attributes = ['key', 'name', 'description', 'remote', 'componentSetId']
        
        for attr in comp_attributes:
            if attr in comp_data:
                comp_item.set(attr, str(comp_data[attr]))
                
        # Process documentation links
        if 'documentationLinks' in comp_data and isinstance(comp_data['documentationLinks'], list):
            for link in comp_data['documentationLinks']:
                link_elem = ET.SubElement(comp_item, '{%s}documentationLinks' % self.nsmap['figmaMM'])
                # If link is a string, use it directly, otherwise convert to string
                if isinstance(link, str):
                    link_elem.text = link
                else:
                    link_elem.text = str(link)