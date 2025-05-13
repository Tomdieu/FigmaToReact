package com.figma.transformer;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.eclipse.m2m.atl.core.ATLCoreException;
import org.eclipse.m2m.atl.core.IExtractor;
import org.eclipse.m2m.atl.core.IInjector;
import org.eclipse.m2m.atl.core.IModel;
import org.eclipse.m2m.atl.core.IReferenceModel;
import org.eclipse.m2m.atl.core.ModelFactory;
import org.eclipse.m2m.atl.core.emf.EMFExtractor;
import org.eclipse.m2m.atl.core.emf.EMFInjector;
import org.eclipse.m2m.atl.core.emf.EMFModelFactory;
import org.eclipse.m2m.atl.core.launch.ILauncher;
import org.eclipse.m2m.atl.engine.emfvm.launch.EMFVMLauncher;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class ATLRunner {

    public static void main(String[] args) {
        if (args.length < 6) {
            System.err.println("Usage: java -jar atl-runner.jar <transformation.asm> <source.xmi> <target.xmi> <sourceMetamodel.ecore> <targetMetamodel.ecore> <sourceModelName> <targetModelName>");
            System.err.println("Example: java -jar atl-runner.jar tranform.asm figma_instance.xmi react_new_instance.xmi figma_meta_model.ecore react_meta_model.ecore FigmaMM ReactMM");
            System.exit(1);
        }

        String atlFile = args[0];
        String sourceModel = args[1];
        String targetModel = args[2];
        String sourceMetamodel = args[3];
        String targetMetamodel = args[4];
        String sourceModelName = args.length > 5 ? args[5] : "IN";
        String targetModelName = args.length > 6 ? args[6] : "OUT";

        ATLRunner runner = new ATLRunner();
        try {
            runner.transform(atlFile, sourceModel, targetModel, sourceMetamodel, targetMetamodel, sourceModelName, targetModelName);
            System.out.println("\\n✓ Transformation completed successfully!");
            System.exit(0);
        } catch (Exception e) {
            System.err.println("\\nError during transformation: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    public void transform(String atlFile, String sourceModelPath, String targetModelPath,
                          String sourceMetamodelPath, String targetMetamodelPath,
                          String sourceModelName, String targetModelName) throws Exception {
        
        System.out.println("=".repeat(80));
        System.out.println("ATL Model Transformation Runner");
        System.out.println("=".repeat(80));
        System.out.println("Transformation:      " + atlFile);
        System.out.println("Source Model:        " + sourceModelPath);
        System.out.println("Target Model:        " + targetModelPath);
        System.out.println("Source Metamodel:    " + sourceMetamodelPath);
        System.out.println("Target Metamodel:    " + targetMetamodelPath);
        System.out.println("=".repeat(80));

        // Initialize EMF
        System.out.println("\\n[1/6] Initializing EMF...");
        ResourceSet resourceSet = new ResourceSetImpl();
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("xmi", new XMIResourceFactoryImpl());
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("*", new XMIResourceFactoryImpl());
        System.out.println("    ✓ EMF initialized");

        // Load metamodels
        System.out.println("\\n[2/6] Loading metamodels...");
        ModelFactory modelFactory = new EMFModelFactory();
        IInjector injector = new EMFInjector();

        // Load source metamodel
        IReferenceModel sourceMetamodel = modelFactory.newReferenceModel();
        injector.inject(sourceMetamodel, sourceMetamodelPath);
        System.out.println("    ✓ Source metamodel loaded: " + sourceMetamodelPath);

        // Load target metamodel
        IReferenceModel targetMetamodel = modelFactory.newReferenceModel();
        injector.inject(targetMetamodel, targetMetamodelPath);
        System.out.println("    ✓ Target metamodel loaded: " + targetMetamodelPath);

        // Load source model
        System.out.println("\\n[3/6] Loading source model...");
        IModel sourceModel = modelFactory.newModel(sourceMetamodel);
        injector.inject(sourceModel, sourceModelPath);
        System.out.println("    ✓ Source model loaded: " + sourceModelPath);

        // Create target model
        System.out.println("\\n[4/6] Creating target model...");
        IModel targetModel = modelFactory.newModel(targetMetamodel);
        System.out.println("    ✓ Target model created");

        // Launch transformation
        System.out.println("\\n[5/6] Running ATL transformation...");
        ILauncher launcher = new EMFVMLauncher();
        Map<String, Object> launcherOptions = new HashMap<>();
        launcherOptions.put("allowInterModelReferences", "true");
        launcherOptions.put("supportUML2Stereotypes", "true");
        
        launcher.initialize(launcherOptions);
        launcher.addInModel(sourceModel, sourceModelName, sourceModelName + "MM");
        launcher.addOutModel(targetModel, targetModelName, targetModelName + "MM");

        try (InputStream atlStream = new FileInputStream(atlFile)) {
            launcher.launch(ILauncher.RUN_MODE, null, launcherOptions, atlStream);
        }
        System.out.println("    ✓ Transformation executed");

        // Save target model
        System.out.println("\\n[6/6] Saving target model...");
        IExtractor extractor = new EMFExtractor();
        extractor.extract(targetModel, targetModelPath);
        System.out.println("    ✓ Target model saved: " + targetModelPath);

        System.out.println("\\n" + "=".repeat(80));
    }
}
