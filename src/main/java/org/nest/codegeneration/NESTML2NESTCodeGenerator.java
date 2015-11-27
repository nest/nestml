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
import de.se_rwth.commons.logging.Log;
import org.apache.commons.io.FileUtils;
import org.nest.codegeneration.converters.GSLReferenceConverter;
import org.nest.codegeneration.converters.NESTReferenceConverter;
import org.nest.codegeneration.helpers.*;
import org.nest.codegeneration.printers.NESTMLDynamicsPrinter;
import org.nest.codegeneration.printers.NESTMLFunctionPrinter;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTNeuronList;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.utils.ASTNodes;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

import static de.se_rwth.commons.Names.getPathFromPackage;
import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Generates C++ Implementation and model integration code for NEST.
 * @author plotnikov
 */
public class NESTML2NESTCodeGenerator {
  private final String LOG_NAME = NESTML2NESTCodeGenerator.class.getName();
  private final ODEProcessor odeProcessor = new ODEProcessor();
  private final NESTReferenceConverter converter;
  private final ExpressionsPrettyPrinter expressionsPrinter;
  private final PredefinedTypesFactory typesFactory;
  private final NESTMLScopeCreator scopeCreator;

  public NESTML2NESTCodeGenerator(
      final PredefinedTypesFactory typesFactory,
      final NESTMLScopeCreator scopeCreator) {
    this.scopeCreator = scopeCreator;
    this.typesFactory = typesFactory;
    converter = new NESTReferenceConverter(typesFactory);
    expressionsPrinter = new ExpressionsPrettyPrinter(converter);

  }

  public void generateNESTCode(
      final ASTNESTMLCompilationUnit root,
      final Path outputBase) {
    Log.info(
        "Starts processing of the model: " + ASTNodes.toString(root.getPackageName()),
        LOG_NAME);
    final ASTNESTMLCompilationUnit workingVersion;
    workingVersion = transformOdeToSolution(root, scopeCreator, outputBase);
    generateHeader(workingVersion, outputBase);
    generateClassImplementation(workingVersion, outputBase);
    generateNestModuleCode(workingVersion, outputBase);

    Log.info(
        "Successfully generated NEST code for" + ASTNodes.toString(root.getPackageName()),
        LOG_NAME);
  }

  public ASTNESTMLCompilationUnit transformOdeToSolution(
      final ASTNESTMLCompilationUnit root,
      final NESTMLScopeCreator scopeCreator,
      final Path outputBase) {
    final String moduleName = ASTNodes.toString(root.getPackageName());
    final Path modulePath = Paths.get(outputBase.toString(), getPathFromPackage(moduleName));

    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    if (astBodyDecorator.getOdeDefinition().isPresent()) {
      if (astBodyDecorator.getOdeDefinition().get().getODEs().size() > 1) {
        return root;
      }

    }
    ASTNESTMLCompilationUnit withSolvedOde = odeProcessor.process(root, modulePath);

    try {
      final Path outputTmpPath = Paths.get(outputBase.toString(), "tmp.nestml");
      printModelToFile(withSolvedOde, outputTmpPath.toString());
      withSolvedOde = createNESTMLCompilationUnitMCParser().parse(outputTmpPath.toString()).get();
      scopeCreator.runSymbolTableCreator(withSolvedOde);
      return withSolvedOde;
    }
    catch (IOException e) {
      throw  new RuntimeException(e);
    }

  }

  public void generateHeader(
      final ASTNESTMLCompilationUnit compilationUnit,
      final Path outputFolder) {
    final String moduleName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());

    final GeneratorSetup setup = new GeneratorSetup(new File(outputFolder.toString()));
    final GlobalExtensionManagement glex = getGlexConfiguration();
    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    for (ASTNeuron neuron : compilationUnit.getNeurons()) {
      setNeuronGenerationParameter(glex, typesFactory, neuron, moduleName);
      final Path outputFile = Paths.get(getPathFromPackage(moduleName), neuron.getName() + ".h");

      // TODO: how do I find out the call was successful?
      generator.generate("org.nest.nestml.neuron.NeuronHeader", outputFile, neuron);
    }
    
  }

  public void generateODECodeForGSL(
      ASTNESTMLCompilationUnit root, ASTNeuron astNeuron, final ASTOdeDeclaration odeDeclaration,
      final Path outputFolder) {

    final GeneratorSetup setup = new GeneratorSetup(new File(outputFolder.toString()));
    final GlobalExtensionManagement glex = getGlexConfiguration();
    setup.setGlex(glex);
    final String moduleName = Names.getQualifiedName(root.getPackageName().getParts());
    setNeuronGenerationParameter(glex, typesFactory, astNeuron, moduleName);


    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(astNeuron.getBody());
    final ASTOdeDeclaration astOdeDeclaration = astBodyDecorator.getOdeDefinition().get();

    glex.setGlobalValue("ODEs", astOdeDeclaration.getODEs());
    glex.setGlobalValue("EQs", astOdeDeclaration.getEqs());


    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path outputFile = Paths.get(outputFolder.toString(), "tmp.cpp");


    // TODO: how do I find out the call was successful?
    generator.generate("org.nest.nestml.function.GSLDifferentiationFunction", outputFile, odeDeclaration);

  }

  public void generateClassImplementation(
      final ASTNESTMLCompilationUnit compilationUnit,
      final Path outputDirectory) {
    final String moduleName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());

    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));
    final GlobalExtensionManagement glex = getGlexConfiguration();
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

  public void generateNestModuleCode(
      final ASTNESTMLCompilationUnit compilationUnit,
      final Path outputDirectory) {
    final String fullName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());
    final String moduleName = Names.getSimpleName(fullName);

    final ASTNeuronList neurons = compilationUnit.getNeurons();
    final List<String> neuronModelNames = neurons
        .stream()
        .map(ASTNeuron::getName)
        .collect(Collectors.toList());

    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));
    setup.setTracing(false);

    final GlobalExtensionManagement glex = getGlexConfiguration();
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

  private void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputFolderBase) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputFolderBase);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputFolderBase, e);
    }

  }

  public GlobalExtensionManagement getGlexConfiguration() {
    final GlobalExtensionManagement glex = new GlobalExtensionManagement();
    glex.setGlobalValue("expressionsPrinter", expressionsPrinter);
    glex.setGlobalValue("functionCallConverter", converter);
    return glex;
  }


  private void setNeuronGenerationParameter(
      final GlobalExtensionManagement glex,
      final PredefinedTypesFactory typesFactory,
      final ASTNeuron neuron,
      final String moduleName) {
    setSolverType(glex, neuron);

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

    final GSLReferenceConverter converter = new GSLReferenceConverter();
    final ExpressionsPrettyPrinter expressionsPrinter = new ExpressionsPrettyPrinter(converter);
    glex.setGlobalValue("expressionsPrinterForGSL", expressionsPrinter);

  }

  private void setSolverType(GlobalExtensionManagement glex, ASTNeuron neuron) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(neuron.getBody());
    glex.setGlobalValue("useGSL", false);
    if (astBodyDecorator.getOdeDefinition().isPresent()) {
      if (astBodyDecorator.getOdeDefinition().get().getODEs().size() > 1) {
        glex.setGlobalValue("useGSL", true);
        glex.setGlobalValue("ODEs", astBodyDecorator.getOdeDefinition().get().getODEs());
      }

    }

  }

  private static String convertToCppNamespaceConvention(String fqnName) {
    return fqnName.replace(".", "::");
  }


}
