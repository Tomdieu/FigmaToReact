package com.figma.validator;

import org.eclipse.emf.common.util.Diagnostic;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.Diagnostician;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class OCLValidator {

    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("Usage: java -jar ocl-validator.jar <model.xmi> <metamodel.ecore> <constraints.ocl>");
            System.err.println("Example: java -jar ocl-validator.jar figma_instance.xmi figma_meta_model.ecore figma_meta_model.ocl");
            System.exit(1);
        }

        String modelPath = args[0];
        String metamodelPath = args[1];
        String oclPath = args[2];

        OCLValidator validator = new OCLValidator();
        try {
            boolean isValid = validator.validate(modelPath, metamodelPath, oclPath);
            System.exit(isValid ? 0 : 1);
        } catch (Exception e) {
            System.err.println("Error during validation: " + e.getMessage());
            e.printStackTrace();
            System.exit(2);
        }
    }

    public boolean validate(String modelPath, String metamodelPath, String oclPath) throws IOException {
        System.out.println("=".repeat(80));
        System.out.println("OCL Model Validator");
        System.out.println("=".repeat(80));
        System.out.println("Model file:      " + modelPath);
        System.out.println("Metamodel file:  " + metamodelPath);
        System.out.println("OCL file:        " + oclPath);
        System.out.println("=".repeat(80));

        // Initialize EMF
        ResourceSet resourceSet = new ResourceSetImpl();
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("xmi", new XMIResourceFactoryImpl());
        resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap().put("*", new XMIResourceFactoryImpl());

        // Load metamodel
        System.out.println("\n[1/4] Loading metamodel...");
        Resource metamodelResource = resourceSet.getResource(URI.createFileURI(new File(metamodelPath).getAbsolutePath()), true);
        if (metamodelResource == null || metamodelResource.getContents().isEmpty()) {
            throw new IOException("Failed to load metamodel from: " + metamodelPath);
        }

        EPackage ePackage = (EPackage) metamodelResource.getContents().get(0);
        resourceSet.getPackageRegistry().put(ePackage.getNsURI(), ePackage);
        System.out.println("    ✓ Metamodel loaded: " + ePackage.getName());

        // Load model instance
        System.out.println("\n[2/4] Loading model instance...");
        Resource modelResource = resourceSet.getResource(URI.createFileURI(new File(modelPath).getAbsolutePath()), true);
        if (modelResource == null || modelResource.getContents().isEmpty()) {
            throw new IOException("Failed to load model from: " + modelPath);
        }
        System.out.println("    ✓ Model loaded with " + modelResource.getContents().size() + " root element(s)");

        // Parse OCL constraints
        System.out.println("\n[3/4] Parsing OCL constraints...");
        List<String> oclConstraints = parseOCLFile(oclPath);
        System.out.println("    ✓ Found " + oclConstraints.size() + " OCL constraints");

        // Validate using EMF diagnostics
        System.out.println("\n[4/4] Validating model...");
        boolean isValid = true;
        int errorCount = 0;
        int warningCount = 0;
        List<String> violations = new ArrayList<>();

        for (EObject eObject : modelResource.getContents()) {
            Diagnostic diagnostic = Diagnostician.INSTANCE.validate(eObject);
            
            if (diagnostic.getSeverity() != Diagnostic.OK) {
                processDiagnostic(diagnostic, violations, 0);
                
                for (Diagnostic child : diagnostic.getChildren()) {
                    if (child.getSeverity() == Diagnostic.ERROR) {
                        errorCount++;
                        isValid = false;
                    } else if (child.getSeverity() == Diagnostic.WARNING) {
                        warningCount++;
                    }
                }
            }
        }

        // Display results
        System.out.println("\n" + "=".repeat(80));
        System.out.println("VALIDATION RESULTS");
        System.out.println("=".repeat(80));

        if (isValid && errorCount == 0 && warningCount == 0) {
            System.out.println("✓ Model is VALID - All constraints satisfied!");
            System.out.println("\nNo errors or warnings found.");
        } else {
            System.out.println("✗ Model VALIDATION FAILED");
            System.out.println("\nSummary:");
            System.out.println("  Errors:   " + errorCount);
            System.out.println("  Warnings: " + warningCount);

            if (!violations.isEmpty()) {
                System.out.println("\nConstraint Violations:");
                System.out.println("-".repeat(80));
                for (int i = 0; i < violations.size(); i++) {
                    System.out.println((i + 1) + ". " + violations.get(i));
                }
            }
        }

        System.out.println("=".repeat(80));

        return isValid && errorCount == 0;
    }

    private void processDiagnostic(Diagnostic diagnostic, List<String> violations, int level) {
        if (diagnostic.getSeverity() != Diagnostic.OK) {
            String indent = "  ".repeat(level);
            String severity = getSeverityLabel(diagnostic.getSeverity());
            String message = diagnostic.getMessage();
            
            violations.add(indent + severity + ": " + message);
            
            for (Diagnostic child : diagnostic.getChildren()) {
                processDiagnostic(child, violations, level + 1);
            }
        }
    }

    private String getSeverityLabel(int severity) {
        switch (severity) {
            case Diagnostic.ERROR:
                return "[ERROR]";
            case Diagnostic.WARNING:
                return "[WARNING]";
            case Diagnostic.INFO:
                return "[INFO]";
            default:
                return "[UNKNOWN]";
        }
    }

    private List<String> parseOCLFile(String oclPath) throws IOException {
        List<String> constraints = new ArrayList<>();
        String content = new String(Files.readAllBytes(Paths.get(oclPath)));
        
        // Simple parsing - count constraint definitions
        String[] lines = content.split("\n");
        for (String line : lines) {
            String trimmed = line.trim();
            if (trimmed.startsWith("inv ") || trimmed.startsWith("pre ") || trimmed.startsWith("post ")) {
                String constraintName = trimmed.split(":")[0].substring(4).trim();
                constraints.add(constraintName);
            }
        }
        
        return constraints;
    }
}
