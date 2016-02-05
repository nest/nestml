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
import org.apache.commons.io.FileUtils;
import org.nest.codegeneration.converters.GSLReferenceConverter;
import org.nest.codegeneration.converters.NESTReferenceConverter;
import org.nest.codegeneration.helpers.*;
import org.nest.codegeneration.printers.NESTMLFunctionPrinter;
import org.nest.codegeneration.sympy.AliasSolverScriptGenerator;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.utils.ASTNodes;
import org.nest.utils.NESTMLSymbols;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static de.se_rwth.commons.Names.getPathFromPackage;
import static de.se_rwth.commons.logging.Log.info;

/**
 * Generates C++ implementation and model integration code for NEST.
 * @author plotnikov
 */
public class NESTCodeGenerator {
  private final String LOG_NAME = NESTCodeGenerator.class.getName();
  private final ODEProcessor odeProcessor;
  private final NESTReferenceConverter converter = new NESTReferenceConverter();
  private final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter(converter);
  private final NESTMLScopeCreator scopeCreator;

  public NESTCodeGenerator(final NESTMLScopeCreator scopeCreator, final ODEProcessor odeProcessor) {
    this.scopeCreator = scopeCreator;
    this.odeProcessor= odeProcessor;
  }

  public NESTCodeGenerator(final NESTMLScopeCreator scopeCreator) {
    this.scopeCreator = scopeCreator;
    this.odeProcessor= new ODEProcessor();
  }

  public void analyseAndGenerate(
      final ASTNESTMLCompilationUnit root,
      final Path outputBase) {
    info("Starts processing of the model: " + root.getFullName(), LOG_NAME);
    ASTNESTMLCompilationUnit workingVersion;

    workingVersion = computeSolutionForODE(root, scopeCreator, outputBase);
    // TODO re-enable me workingVersion = computeSetterForAliases(workingVersion, scopeCreator, outputBase);
    generateNESTCode(workingVersion, outputBase);

    info("Successfully generated NEST code for: " + root.getFullName(), LOG_NAME);
  }

  protected ASTNESTMLCompilationUnit computeSolutionForODE(
      final ASTNESTMLCompilationUnit root,
      final NESTMLScopeCreator scopeCreator,
      final Path outputBase) {
    // TODO: it makes no sense anymore. Print it flatly
    final String moduleName = root.getFullName();
    final Path modulePath = Paths.get(outputBase.toString(), getPathFromPackage(moduleName));

    final ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    final Optional<ASTOdeDeclaration> odesBlock = bodyDecorator.getEquations();
    if (odesBlock.isPresent()) {
      if (odesBlock.get().getEqs().size() == 0) {
        info("The model will be solved numerically with a GSL solver.", LOG_NAME);
        return root;
      }

      ASTNESTMLCompilationUnit withSolvedOde = odeProcessor.solveODE(root, modulePath);

      return printAndReadModel(scopeCreator, modulePath, withSolvedOde);
    }
    else {
      return root;
    }


  }

  protected ASTNESTMLCompilationUnit computeSetterForAliases(
      final ASTNESTMLCompilationUnit root,
      final NESTMLScopeCreator scopeCreator,
      final Path outputBase) {
    final AliasSolverScriptGenerator generator = new AliasSolverScriptGenerator();
    final Optional<Path> inverterScript = generator.generateAliasInverter(root.getNeurons().get(0), outputBase);

    final String moduleName = root.getFullName();
    final Path modulePath = Paths.get(outputBase.toString(), getPathFromPackage(moduleName));
    return printAndReadModel(scopeCreator, modulePath, root);
  }

  /**
   * This action is done for 2 Reasons:
   * a) Technically it is necessary to build a new symbol table
   * b) The model developer can view how the solution was computed.
   * @return New root node of the altered model with an initialized symbol table
   */
  private ASTNESTMLCompilationUnit printAndReadModel(
      final NESTMLScopeCreator scopeCreator,
      final Path modulePath,
      final ASTNESTMLCompilationUnit root) {
    try {
      final Path outputTmpPath = Paths.get(modulePath.toString(), "tmp.nestml");
      printModelToFile(root, outputTmpPath.toString());
      final NESTMLParser parser = new NESTMLParser();

      final ASTNESTMLCompilationUnit withSolvedOde = parser.parseNESTMLCompilationUnit
          (outputTmpPath.toString()).get();
      withSolvedOde.setArtifactName(root.getArtifactName());
      if (root.getPackageName().isPresent()) {
        withSolvedOde.setPackageName(root.getPackageName().get());
      }
      else {
        withSolvedOde.removePackageName();
      }

      scopeCreator.runSymbolTableCreator(withSolvedOde);
      return withSolvedOde;
    }
    catch (IOException e) {
      throw  new RuntimeException(e);
    }
  }

  public void generateNESTCode(
      final ASTNESTMLCompilationUnit workingVersion,
      final Path outputBase) {
    generateHeader(workingVersion, outputBase);
    generateClassImplementation(workingVersion, outputBase);
  }

  public void generateHeader(
      final ASTNESTMLCompilationUnit compilationUnit,
      final Path outputFolder) {
    final String moduleName = compilationUnit.getFullName();

    final GeneratorSetup setup = new GeneratorSetup(new File(outputFolder.toString()));
    final GlobalExtensionManagement glex = getGlexConfiguration();
    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    for (final ASTNeuron neuron : compilationUnit.getNeurons()) {
      setNeuronGenerationParameter(glex, neuron, moduleName);
      final Path outputFile = Paths.get(neuron.getName() + ".h");

      generator.generate("org.nest.nestml.neuron.NeuronHeader", outputFile, neuron);
    }
    
  }

  public void generateClassImplementation(
      final ASTNESTMLCompilationUnit compilationUnit,
      final Path outputBase) {
    final String moduleName = compilationUnit.getFullName();

    final GeneratorSetup setup = new GeneratorSetup(new File(outputBase.toString()));
    final GlobalExtensionManagement glex = getGlexConfiguration();
    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final List<ASTNeuron> neurons = compilationUnit.getNeurons();
    for (ASTNeuron neuron : neurons) {
      setNeuronGenerationParameter(glex, neuron, moduleName);
      final Path classImplementationFile = Paths.get(neuron.getName() + ".cpp");
      // TODO: how do I find out the call was successful?
      generator.generate(
          "org.nest.nestml.neuron.NeuronClass",
          classImplementationFile,
          neuron);
    }

  }

  public void generateNESTModuleCode(
      final List<ASTNESTMLCompilationUnit> modelRoots,
      final String moduleName,
      final Path outputDirectory) {
    final List<ASTNeuron> neurons = modelRoots.stream()
        .flatMap(root -> root.getNeurons().stream())
        .collect(Collectors.toList());
    generateModuleCodeForNeuron(neurons, moduleName, outputDirectory);
  }

  protected void generateModuleCodeForNeuron(
      final List<ASTNeuron> neurons,
      final String moduleName,
      final Path outputDirectory) {

    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));
    setup.setTracing(false);

    final GlobalExtensionManagement glex = getGlexConfiguration();
    glex.setGlobalValue("neurons", neurons);
    glex.setGlobalValue("moduleName", moduleName);
    glex.setGlobalValue("names", new Names());

    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path makefileFile = Paths.get("Makefile.am");
    generator.generate(
        "org.nest.nestml.module.Makefile",
        makefileFile,
        neurons.get(0)); // an arbitrary AST to match the signature

    final Path bootstrappingFile = Paths.get("bootstrap.sh");
    generator.generate(
        "org.nest.nestml.module.Bootstrap",
        bootstrappingFile,
        neurons.get(0)); // an arbitrary AST to match the signature

    final Path configureFile = Paths.get("configure.ac");
    generator.generate(
        "org.nest.nestml.module.Configure",
        configureFile,
        neurons.get(0)); // an arbitrary AST to match the signature

    final Path moduleClass = Paths.get(moduleName + "Config.cpp");
    generator.generate(
        "org.nest.nestml.module.ModuleClass",
        moduleClass,
        neurons.get(0)); // an arbitrary AST to match the signature

    final Path moduleHeader = Paths.get( moduleName + "Config.h");
    generator.generate(
        "org.nest.nestml.module.ModuleHeader",
        moduleHeader,
        neurons.get(0)); // an arbitrary AST to match the signature

    /*
    final Path sliInitFile = Paths.get(
        getPathFromPackage(fullName), "sli", moduleName.toLowerCase() + "-init");
    generator.generate(
        "org.nest.nestml.module.SLI_Init",
        sliInitFile,
        null);*/

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
      final ASTNeuron neuron,
      final String moduleName) {
    setSolverType(glex, neuron);

    final String guard = (moduleName + "." + neuron.getName()).replace(".", "_");
    glex.setGlobalValue("guard", guard);
    glex.setGlobalValue("simpleNeuronName", neuron.getName());

    final String nspPrefix = convertToCppNamespaceConvention(moduleName);
    final NESTMLFunctionPrinter functionPrinter = new NESTMLFunctionPrinter();
    final NESTMLDeclarations declarations = new NESTMLDeclarations();
    glex.setGlobalValue("declarations", new NESTMLDeclarations() );
    glex.setGlobalValue("assignments", new SPLAssignments());
    glex.setGlobalValue("functionPrinter", functionPrinter);
    glex.setGlobalValue("functions", new SPLFunctionCalls());
    glex.setGlobalValue("declarations", declarations);
    glex.setGlobalValue("bufferHelper", new NESTMLBuffers());

    glex.setGlobalValue("nspPrefix", nspPrefix);
    glex.setGlobalValue("outputEvent", NESTMLOutputs.printOutputEvent(neuron));
    glex.setGlobalValue("isOutputEventPresent", NESTMLOutputs.isOutputEventPresent(neuron));
    glex.setGlobalValue("isSpikeInput", NESTMLInputs.isSpikeInput(neuron));
    glex.setGlobalValue("isCurrentInput", NESTMLInputs.isCurrentInput(neuron));
    glex.setGlobalValue("body", new ASTBodyDecorator(neuron.getBody()));

    final GSLReferenceConverter converter = new GSLReferenceConverter();
    final ExpressionsPrettyPrinter expressionsPrinter = new ExpressionsPrettyPrinter(converter);
    glex.setGlobalValue("expressionsPrinterForGSL", expressionsPrinter);
    glex.setGlobalValue("nestmlSymbols", new NESTMLSymbols());
    glex.setGlobalValue("astNodes", new ASTNodes());

  }

  private void setSolverType(GlobalExtensionManagement glex, ASTNeuron neuron) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(neuron.getBody());
    glex.setGlobalValue("useGSL", false);
    if (astBodyDecorator.getEquations().isPresent()) {
      if (astBodyDecorator.getEquations().get().getODEs().size() > 1) {
        glex.setGlobalValue("useGSL", true);
        glex.setGlobalValue("ODEs", astBodyDecorator.getEquations().get().getODEs());
      }

    }

  }

  private static String convertToCppNamespaceConvention(String fqnName) {
    return fqnName.replace(".", "::");
  }


}
