import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Iterator;

public class FigmaToXMIParser {

    private static EPackage figmaMetamodel;

    public static void main(String[] args) {
        String jsonFilePath = "response.json"; // Replace with your JSON file path
        String ecoreModelPath = "meta-model.xml"; // Replace with your Ecore model path
        String outputXmiPath = "output.xmi";  // Replace with your desired output XMI path

        try {
            convertJsonToXmi(jsonFilePath, ecoreModelPath, outputXmiPath);
            System.out.println("Conversion successful! XMI file saved to: " + outputXmiPath);
        } catch (Exception e) {
            System.err.println("Conversion failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void convertJsonToXmi(String jsonFilePath, String ecoreModelPath, String outputXmiPath) throws IOException {
        // 1. Load the Figma Metamodel
        figmaMetamodel = loadMetamodel(ecoreModelPath);

        // 2. Load the JSON file
        String jsonString = new String(Files.readAllBytes(Paths.get(jsonFilePath)));
        JSONObject jsonObject = new JSONObject(jsonString);

        // 3. Create the Root EObject (FigmaApp)
        EObject figmaApp = createEObject("FigmaApp");

        // 4. Populate FigmaApp attributes
        setEAttribute(figmaApp, "name", jsonObject.getString("name"));
        setEAttribute(figmaApp, "lastModified", jsonObject.getString("lastModified"));
        setEAttribute(figmaApp, "thumbnailUrl", jsonObject.optString("thumbnailUrl", null));  // Handle optional fields
        setEAttribute(figmaApp, "version", jsonObject.getString("version"));
        setEAttribute(figmaApp, "editorType", jsonObject.getString("editorType"));

        // 5. Process the 'document' object
        JSONObject documentJson = jsonObject.getJSONObject("document");
        EObject document = processDocument(documentJson);
        setEReference(figmaApp, "document", document); // Set document reference on FigmaApp

        //6. Process Components and componentSets
        processComponentAndComponentSet(figmaApp,jsonObject);
        // 7. Serialize the EMF Model to XMI
        serializeToXMI(figmaApp, outputXmiPath);
    }

    private static void processComponentAndComponentSet(EObject figmaApp, JSONObject jsonObject){
        if(jsonObject.has("components")){
            JSONObject componentJson = jsonObject.getJSONObject("components");
            Iterator<String> keys = componentJson.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                JSONObject item = componentJson.getJSONObject(key);
                EObject data = createEObject("ComponentData");
                EObject componentItem = createEObject("ComponentItem");

                setEAttribute(componentItem, "key", key);
                setEAttribute(componentItem, "name", item.getString("name"));
                setEAttribute(componentItem, "description", item.optString("description", ""));
                setEAttribute(componentItem, "remote", item.getBoolean("remote"));

                if(item.has("componentSetId")){
                    setEAttribute(componentItem, "componentSetId", item.optString("componentSetId",""));
                }

                setEReference(data,"data",componentItem);
                addEReference(figmaApp, "components", data);
            }
        }

        if(jsonObject.has("componentSets")){
            JSONObject componentSetsJson = jsonObject.getJSONObject("componentSets");
            Iterator<String> keys = componentSetsJson.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                JSONObject item = componentSetsJson.getJSONObject(key);
                EObject data = createEObject("ComponentData");
                EObject componentItem = createEObject("ComponentItem");

                setEAttribute(componentItem, "key", key);
                setEAttribute(componentItem, "name", item.getString("name"));
                setEAttribute(componentItem, "description", item.optString("description", ""));
                setEAttribute(componentItem, "remote", false); // Assuming component sets are never remote

                setEReference(data,"data",componentItem);
                addEReference(figmaApp, "componenSets", data);
            }
        }
    }

    private static EObject processDocument(JSONObject documentJson) {
        EObject document = createEObject("Document");

        setEAttribute(document, "id", documentJson.getString("id"));
        setEAttribute(document, "name", documentJson.getString("name"));
        setEAttribute(document, "type", documentJson.getString("type"));
        setEAttribute(document, "scrollBehavior", documentJson.getString("scrollBehavior"));

        // Process children recursively
        if (documentJson.has("children")) {
            JSONArray childrenJsonArray = documentJson.getJSONArray("children");
            for (int i = 0; i < childrenJsonArray.length(); i++) {
                JSONObject childJson = childrenJsonArray.getJSONObject(i);
                EObject child = processChild(childJson);
                addEReference(document, "children", child); //Adds EReference Children to list of children
            }
        }

        return document;
    }

    private static EObject processChild(JSONObject childJson) {
        String type = childJson.getString("type");
        EObject child = createEObject(type);

        setEAttribute(child, "id", childJson.getString("id"));
        setEAttribute(child, "name", childJson.getString("name"));
        setEAttribute(child, "type", type);

        // Process common properties based on the Ecore model, handling optional values
        setEAttribute(child, "scrollBehavior", childJson.optString("scrollBehavior", "SCROLLS"));

        // Process the absoluteBoundingBox
        if (childJson.has("absoluteBoundingBox")) {
            JSONObject boundingBoxJson = childJson.getJSONObject("absoluteBoundingBox");
            EObject boundingBox = createDimensions(boundingBoxJson);
            setEReference(child, "absoluteBoundingBox", boundingBox);
        }

        // Process the absoluteRenderBounds
        if (childJson.has("absoluteRenderBounds")) {
            JSONObject renderBoundsJson = childJson.getJSONObject("absoluteRenderBounds");
            EObject renderBounds = createDimensions(renderBoundsJson);
            setEReference(child, "absoluteRenderBounds", renderBounds);
        }

        // Process Constraints
        if(childJson.has("constraints")){
            JSONObject constraintJson = childJson.getJSONObject("constraints");
            EObject constraint = createConstraints(constraintJson);
            setEReference(child,"constraints", constraint);
        }

        //Process Interaction
        if(childJson.has("interactions")){
            JSONArray interactionJsonArray = childJson.getJSONArray("interactions");
            for(int i = 0; i < interactionJsonArray.length(); i++){
                JSONObject interactionJson = interactionJsonArray.getJSONObject(i);
                EObject interaction = createEObject("Interaction");
                //Process Trigger
                if(interactionJson.has("trigger")){
                    JSONObject triggerJson = interactionJson.getJSONObject("trigger");
                    EObject trigger = createEObject("Trigger");
                    setEAttribute(trigger, "type", triggerJson.getString("type"));
                    setEReference(interaction,"trigger", trigger);
                }
                addEReference(child, "interactions", interaction);
            }
        }

        //Process styles for TEXT elements
        if("TEXT".equals(type) && childJson.has("style")){
            JSONObject styleJson = childJson.getJSONObject("style");
            EObject style = createEObject("Style");
            setEAttribute(style,"fontFamily",styleJson.getString("fontFamily"));
            setEAttribute(style, "fontPostScriptName", styleJson.optString("fontPostScriptName","Inter-Regular")); //Optional values
            setEAttribute(style, "fontSize", styleJson.getDouble("fontSize"));
            setEAttribute(style, "fontWeight", styleJson.getInt("fontWeight"));
            setEAttribute(style, "letterSpacing", styleJson.getDouble("letterSpacing"));
            setEAttribute(style, "lineHeightPx", styleJson.getDouble("lineHeightPx"));
            setEAttribute(style, "lineHeightPercent", styleJson.getDouble("lineHeightPercent"));
            setEAttribute(style, "textAlignHorizontal", styleJson.getString("textAlignHorizontal"));
            setEAttribute(style, "textAlignVertical", styleJson.getString("textAlignVertical"));
            setEReference(child, "style",style);
            setEAttribute(child, "characters", childJson.getString("characters"));
        }

       // Process Background and Strokes (assuming similar structure)
        if (childJson.has("fills")) {
            JSONArray fillsJsonArray = childJson.getJSONArray("fills");
            for (int i = 0; i < fillsJsonArray.length(); i++) {
                JSONObject fillJson = fillsJsonArray.getJSONObject(i);
                EObject fill = createBackground(fillJson);
                addEReference(child, "fills", fill);
            }
        }

        if (childJson.has("strokes")) {
            JSONArray strokesJsonArray = childJson.getJSONArray("strokes");
            for (int i = 0; i < strokesJsonArray.length(); i++) {
                JSONObject strokeJson = strokesJsonArray.getJSONObject(i);
                EObject stroke = createBackground(strokeJson);
                addEReference(child, "strokes", stroke);
            }
        }

        // Process children recursively
        if (childJson.has("children")) {
            JSONArray childrenJsonArray = childJson.getJSONArray("children");
            for (int i = 0; i < childrenJsonArray.length(); i++) {
                JSONObject nestedChildJson = childrenJsonArray.getJSONObject(i);
                EObject nestedChild = processChild(nestedChildJson);
                addEReference(child, "children", nestedChild); // Add EReference Children to list of children
            }
        }

        return child;
    }

    private static EObject createBackground(JSONObject backgroundJson) {
        EObject background = createEObject("Background");
        setEAttribute(background, "blendMode", backgroundJson.getString("blendMode"));
        setEAttribute(background,"type", "SOLID");

        if (backgroundJson.has("color")) {
            JSONObject colorJson = backgroundJson.getJSONObject("color");
            EObject color = createColor(colorJson);
            setEReference(background, "color", color);
        }
         return background;
    }

    private static EObject createDimensions(JSONObject dimensionJson) {
        EObject dimensions = createEObject("Dimensions");
        setEAttribute(dimensions, "x", dimensionJson.getDouble("x"));
        setEAttribute(dimensions, "y", dimensionJson.getDouble("y"));
        setEAttribute(dimensions, "width", dimensionJson.getDouble("width"));
        setEAttribute(dimensions, "height", dimensionJson.getDouble("height"));
        return dimensions;
    }

    private static EObject createConstraints(JSONObject constraintJson){
        EObject constraint = createEObject("Constraints");
        setEAttribute(constraint, "horizontal", constraintJson.getString("horizontal"));
        setEAttribute(constraint, "vertical", constraintJson.getString("vertical"));
        return constraint;
    }

    private static EObject createColor(JSONObject colorJson) {
        EObject color = createEObject("Color");
        setEAttribute(color, "r", colorJson.getDouble("r"));
        setEAttribute(color, "g", colorJson.getDouble("g"));
        setEAttribute(color, "b", colorJson.getDouble("b"));
        setEAttribute(color, "a", colorJson.getDouble("a"));
        return color;
    }


    private static EPackage loadMetamodel(String ecoreModelPath) {
        ResourceSet resourceSet = new ResourceSetImpl();
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("ecore", new XMIResourceFactoryImpl());
        URI fileURI = URI.createFileURI(new File(ecoreModelPath).getAbsolutePath());
        Resource resource = resourceSet.getResource(fileURI, true);
        return (EPackage) resource.getContents().get(0);
    }

    private static EObject createEObject(String className) {
        EClass eClass = (EClass) figmaMetamodel.getEClassifier(className);
        if (eClass == null) {
            throw new IllegalArgumentException("EClass not found: " + className);
        }
        return figmaMetamodel.getEFactoryInstance().create(eClass);
    }

    private static void setEAttribute(EObject eObject, String attributeName, Object value) {
        if (value != null) {
            eObject.eSet(eObject.eClass().getEStructuralFeature(attributeName), value);
        }
    }

    private static void setEReference(EObject eObject, String referenceName, EObject value) {
         if (value != null) {
            eObject.eSet(eObject.eClass().getEStructuralFeature(referenceName), value);
        }
    }

    private static void addEReference(EObject eObject, String referenceName, EObject value) {
        if (value != null) {
            Object featureValue = eObject.eGet(eObject.eClass().getEStructuralFeature(referenceName));
            if (featureValue instanceof java.util.List) {
                ((java.util.List<EObject>) featureValue).add(value);
            } else {
                throw new IllegalArgumentException("Feature " + referenceName + " is not a list.");
            }
        }
    }

    private static void serializeToXMI(EObject rootEObject, String outputXmiPath) throws IOException {
        ResourceSet resourceSet = new ResourceSetImpl();
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("xmi", new XMIResourceFactoryImpl());
        URI fileURI = URI.createFileURI(new File(outputXmiPath).getAbsolutePath());
        Resource resource = resourceSet.createResource(fileURI);
        resource.getContents().add(rootEObject);
        resource.save(null);
    }
}