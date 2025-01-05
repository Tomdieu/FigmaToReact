import java.io.*;
import org.eclipse.emf.ecore.*;
import org.eclipse.emf.ecore.resource.*;
import org.eclipse.emf.ecore.xmi.*;
import org.json.*;

public class FigmaToXMIConverter {
    private EPackage figmaMetamodel;
    private ResourceSet resourceSet;

    public FigmaToXMIConverter(String metamodelPath) {
        // Initialize EMF Resource Set
        resourceSet = new ResourceSetImpl();
        // Load your Figma metamodel
        Resource metamodelResource = resourceSet.getResource(
            URI.createFileURI(metamodelPath), true);
        figmaMetamodel = (EPackage) metamodelResource.getContents().get(0);
    }

    public void convert(String jsonInput, String xmiOutput) {
        try {
            // Parse Figma JSON
            JSONObject figmaJson = new JSONObject(new String(
                Files.readAllBytes(Paths.get(jsonInput))));
            
            // Create new EMF Resource for the output XMI
            Resource xmiResource = resourceSet.createResource(
                URI.createFileURI(xmiOutput));
            
            // Create root element based on your metamodel
            EClass documentClass = (EClass) figmaMetamodel.getEClassifier("FigmaDocument");
            EObject rootElement = figmaMetamodel.getEFactoryInstance().create(documentClass);
            
            // Process Figma JSON structure
            processDocument(figmaJson, rootElement);
            
            // Save as XMI
            xmiResource.getContents().add(rootElement);
            xmiResource.save(Collections.EMPTY_MAP);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void processDocument(JSONObject json, EObject root) {
        // Process document properties
        setAttributeIfExists(root, "name", json, "name");
        
        // Process components
        if (json.has("children")) {
            JSONArray children = json.getJSONArray("children");
            for (int i = 0; i < children.length(); i++) {
                JSONObject child = children.getJSONObject(i);
                processComponent(child, root);
            }
        }
    }

    private void processComponent(JSONObject json, EObject parent) {
        String type = json.getString("type");
        
        // Create appropriate component based on type
        EClass componentClass = (EClass) figmaMetamodel.getEClassifier(
            getMetamodelClassName(type));
        EObject component = figmaMetamodel.getEFactoryInstance().create(componentClass);
        
        // Set common attributes
        setAttributeIfExists(component, "id", json, "id");
        setAttributeIfExists(component, "name", json, "name");
        
        // Process style properties
        if (json.has("style")) {
            processStyle(json.getJSONObject("style"), component);
        }
        
        // Add component to parent's children
        EReference childrenRef = (EReference) parent.eClass()
            .getEStructuralFeature("children");
        @SuppressWarnings("unchecked")
        List<EObject> children = (List<EObject>) parent.eGet(childrenRef);
        children.add(component);
        
        // Process nested components
        if (json.has("children")) {
            JSONArray childrenArray = json.getJSONArray("children");
            for (int i = 0; i < childrenArray.length(); i++) {
                processComponent(childrenArray.getJSONObject(i), component);
            }
        }
    }

    private void processStyle(JSONObject style, EObject component) {
        EClass styleClass = (EClass) figmaMetamodel.getEClassifier("Style");
        EObject styleObject = figmaMetamodel.getEFactoryInstance().create(styleClass);
        
        // Set style properties based on your metamodel
        setAttributeIfExists(styleObject, "backgroundColor", style, "backgroundColor");
        setAttributeIfExists(styleObject, "color", style, "color");
        setAttributeIfExists(styleObject, "fontSize", style, "fontSize");
        // Add more style properties as needed
        
        // Link style to component
        EReference styleRef = (EReference) component.eClass()
            .getEStructuralFeature("style");
        component.eSet(styleRef, styleObject);
    }

    private void setAttributeIfExists(EObject object, String attributeName, 
                                    JSONObject json, String jsonKey) {
        if (json.has(jsonKey)) {
            EAttribute attribute = (EAttribute) object.eClass()
                .getEStructuralFeature(attributeName);
            if (attribute != null) {
                object.eSet(attribute, json.get(jsonKey));
            }
        }
    }

    private String getMetamodelClassName(String figmaType) {
        // Map Figma types to your metamodel classes
        switch (figmaType) {
            case "FRAME": return "Frame";
            case "GROUP": return "Group";
            case "RECTANGLE": return "Rectangle";
            case "TEXT": return "Text";
            // Add more mappings as needed
            default: return "Component";
        }
    }
}