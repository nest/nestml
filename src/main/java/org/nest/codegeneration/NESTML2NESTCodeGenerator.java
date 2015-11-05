/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.Names;
import org.nest.codegeneration.helpers.*;
import org.nest.codegeneration.printers.NESTMLDynamicsPrinter;
import org.nest.codegeneration.printers.NESTMLFunctionPrinter;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTNeuronList;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

import static de.se_rwth.commons.Names.getPathFromPackage;

/**
 * Generates C++ Implementation and model integration code for NEST.
 * @author plotnikov
 */
public class NESTML2NESTCodeGenerator {
  
  public static void generateHeader(
      final GlobalExtensionManagement glex,
      final ASTNESTMLCompilationUnit compilationUnit,
      final PredefinedTypesFactory typesFactory,
      final File outputDirectory) {
    final String moduleName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());

    final GeneratorSetup setup = new GeneratorSetup(outputDirectory);
    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    for (ASTNeuron neuron : compilationUnit.getNeurons()) {
      setNeuronGenerationParameter(glex, typesFactory, neuron, moduleName);
      final Path outputFile = Paths.get(getPathFromPackage(moduleName), neuron.getName() + ".h");

      // TODO: how do I find out the call was successful?
      generator.generate("org.nest.nestml.neuron.NeuronHeader", outputFile, neuron);
    }
    
  }

  public static void generateClassImplementation(final GlobalExtensionManagement glex,
                                                 final PredefinedTypesFactory typesFactory,
                                                 final ASTNESTMLCompilationUnit compilationUnit,
                                                 final File outputDirectory) {
    final String moduleName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());

    final GeneratorSetup setup = new GeneratorSetup(outputDirectory);
    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final ASTNeuronList neurons = compilationUnit.getNeurons();
    for (ASTNeuron neuron : neurons) {
      setNeuronGenerationParameter(glex, typesFactory, neuron, moduleName);
      final Path classImplementationFile = Paths.get(
          getPathFromPackage(moduleName), neuron.getName() + ".cpp");
      // TODO: how do I find out the call was successful?
      generator.generate(
          "org.nest.nestml.neuron.NeuronClass",
          classImplementationFile,
          neuron);
    }

  }

  public static void generateCodeForModelIntegrationInNest(
      final GlobalExtensionManagement glex,
      final ASTNESTMLCompilationUnit compilationUnit,
      final File outputDirectory) {
    final String fullName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());
    final String moduleName = Names.getSimpleName(fullName);

    final ASTNeuronList neurons = compilationUnit.getNeurons();
    final List<String> neuronModelNames = neurons
        .stream()
        .map(ASTNeuron::getName)
        .collect(Collectors.toList());

    final GeneratorSetup setup = new GeneratorSetup(outputDirectory);
    setup.setTracing(false);

    glex.setGlobalValue("moduleName", moduleName);
    glex.setGlobalValue("packageName", fullName);
    glex.setGlobalValue("neuronModelNames", neuronModelNames);

    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path makefileFile = Paths.get(getPathFromPackage(fullName), "Makefile.am");
    generator.generate(
        "org.nest.nestml.module.Makefile",
        makefileFile,
        compilationUnit);

    final Path bootstrappingFile = Paths.get(getPathFromPackage(fullName), "bootstrap.sh");
    generator.generate(
        "org.nest.nestml.module.Bootstrap",
        bootstrappingFile,
        compilationUnit);

    final Path configureFile = Paths.get(getPathFromPackage(fullName), "configure.ac");
    generator.generate(
        "org.nest.nestml.module.Configure",
        configureFile,
        compilationUnit);

    final Path moduleClass = Paths.get(getPathFromPackage(fullName), moduleName + "Config.cpp");
    generator.generate(
        "org.nest.nestml.module.ModuleClass",
        moduleClass,
        compilationUnit);

    final Path moduleHeader = Paths.get(getPathFromPackage(fullName), moduleName + "Config.h");
    generator.generate(
        "org.nest.nestml.module.ModuleHeader",
        moduleHeader,
        compilationUnit);

    final Path sliInitFile = Paths.get(
        getPathFromPackage(fullName), "sli", moduleName.toLowerCase() + "-init");
    generator.generate(
        "org.nest.nestml.module.SLI_Init",
        sliInitFile,
        compilationUnit);
  }

  private static void setNeuronGenerationParameter(
      final GlobalExtensionManagement glex,
      final PredefinedTypesFactory typesFactory,
      final ASTNeuron neuron,
      final String moduleName) {
    final String guard = (moduleName + "." + neuron.getName()).replace(".", "_");
    glex.setGlobalValue("guard", guard);
    glex.setGlobalValue("simpleNeuronName", neuron.getName());

    final String nspPrefix = convertToCppNamespaceConvention(moduleName);
    final NESTMLFunctionPrinter functionPrinter = new NESTMLFunctionPrinter(typesFactory);
    final NESTMLDeclarations declarations = new NESTMLDeclarations(typesFactory);
    final NESTMLDynamicsPrinter dynamicsHelper = new NESTMLDynamicsPrinter(typesFactory);

    glex.setGlobalValue("declarations", new NESTMLDeclarations(typesFactory) );
    glex.setGlobalValue("assignmentHelper", new SPLVariableGetterSetterHelper());
    glex.setGlobalValue("typesFactory", typesFactory);
    glex.setGlobalValue("functionPrinter", functionPrinter);
    glex.setGlobalValue("declarations", declarations);
    glex.setGlobalValue("dynamicsHelper", dynamicsHelper);
    glex.setGlobalValue("bufferHelper", new NESTMLBuffers(typesFactory));

    glex.setGlobalValue("nspPrefix", nspPrefix);
    glex.setGlobalValue("outputEvent", NESTMLOutputs.printOutputEvent(neuron));
    glex.setGlobalValue("isOutputEventPresent", NESTMLOutputs.isOutputEventPresent(neuron));
    glex.setGlobalValue("isSpikeInput", NESTMLInputs.isSpikeInput(neuron));
    glex.setGlobalValue("isCurrentInput", NESTMLInputs.isCurrentInput(neuron));
    glex.setGlobalValue("body", new ASTBodyDecorator(neuron.getBody()));

  }

  private static String convertToCppNamespaceConvention(String fqnName) {
    return fqnName.replace(".", "::");
  }

}

