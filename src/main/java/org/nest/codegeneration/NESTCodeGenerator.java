/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import org.apache.commons.io.FileUtils;
import org.nest.codegeneration.converters.GSLReferenceConverter;
import org.nest.codegeneration.converters.NESTStateBlockReferenceConverter;
import org.nest.spl.prettyprinter.IReferenceConverter;
import org.nest.codegeneration.converters.NESTParameterBlockReferenceConverter;
import org.nest.codegeneration.converters.NESTReferenceConverter;
import org.nest.codegeneration.helpers.*;
import org.nest.codegeneration.helpers.NESTFunctionPrinter;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.codegeneration.sympy.ODETransformer;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.utils.ASTUtils;
import org.nest.utils.NESTMLSymbols;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.info;
import static org.nest.utils.ASTUtils.getAllNeurons;

/**
 * Generates C++ implementation and model integration code for NEST.
 * @author plotnikov
 */
public class NESTCodeGenerator {
  private final String LOG_NAME = NESTCodeGenerator.class.getName();
  private final ODEProcessor odeProcessor;

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

    ASTNESTMLCompilationUnit workingVersion = root;
    for (int i = 0; i < root.getNeurons().size(); ++i) {
      final ASTNeuron solvedNeuron = solveODESInNeuron(root.getNeurons().get(i), outputBase);
      root.getNeurons().set(i, solvedNeuron);
    }

    workingVersion = printAndReadModel(outputBase, workingVersion);
    // TODO re-enable me workingVersion = computeSetterForAliases(workingVersion, scopeCreator, outputBase);
    workingVersion.getNeurons()
        .stream()
        .forEach(astNeuron -> generateNESTCode(astNeuron, outputBase));

    final String msg = "Successfully generated NEST code for: '" + root.getFullName() + "' in: '"
        + outputBase.toAbsolutePath().toString() + "'";
    info(msg, LOG_NAME);
  }

  private ASTNeuron solveODESInNeuron(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final ASTBody astBody = astNeuron.getBody();
    final Optional<ASTOdeDeclaration> odesBlock = astBody.getODEBlock();
    if (odesBlock.isPresent()) {
      if (odesBlock.get().getShapes().size() == 0) {
        info("The model will be solved numerically with a GSL solver.", LOG_NAME);
        return astNeuron;
      }
      else {
        info("The model will be analysed.", LOG_NAME);
        return odeProcessor.solveODE(astNeuron, outputBase);
      }

    }
    else {
      return astNeuron;
    }

  }

  private void generateNESTCode(
      final ASTNeuron astNeuron,
      final Path outputBase) {

    final GlobalExtensionManagement glex = getGlexConfiguration();
    setNeuronGenerationParameter(glex, astNeuron);
    generateHeader(astNeuron, outputBase, glex);
    generateClassImplementation(astNeuron, outputBase, glex);
  }

  private void generateHeader(
      final ASTNeuron astNeuron,
      final Path outputFolder,
      final GlobalExtensionManagement glex) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputFolder.toString()));
    setup.setGlex(glex);

    final GeneratorEngine generator = new GeneratorEngine(setup);
    final Path outputFile = Paths.get(astNeuron.getName() + ".h");
    generator.generate("org.nest.nestml.neuron.NeuronHeader", outputFile, astNeuron);
  }

  private void generateClassImplementation(
      final ASTNeuron astNeuron,
      final Path outputFolder,
      final GlobalExtensionManagement glex) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputFolder.toString()));
    setup.setGlex(glex);
    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path classImplementationFile = Paths.get(astNeuron.getName() + ".cpp");
    generator.generate(
        "org.nest.nestml.neuron.NeuronClass",
        classImplementationFile,
        astNeuron);

  }

  /**
   * This action is done for 2 Reasons:
   * a) Technically it is necessary to build a new symbol table
   * b) The model developer can view how the solution was computed.
   * @return New root node of the altered model with an initialized symbol table
   */
  private ASTNESTMLCompilationUnit printAndReadModel(
      final Path modulePath,
      final ASTNESTMLCompilationUnit root) {
    try {
      final Path outputTmpPath = Paths.get(modulePath.toString(), root.getFullName() + ".nestml");
      printModelToFile(root, outputTmpPath.toString());
      info("Printed analysed model into: " + outputTmpPath, LOG_NAME);
      final NESTMLParser parser = new NESTMLParser(modulePath);

      final ASTNESTMLCompilationUnit withSolvedOde = parser.parseNESTMLCompilationUnit(outputTmpPath.toString()).get();
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

  public void generateNESTModuleCode(
      final List<ASTNESTMLCompilationUnit> modelRoots,
      final String moduleName,
      final Path outputDirectory) {
    final List<ASTNeuron> neurons = getAllNeurons(modelRoots);
    generateModuleCodeForNeurons(neurons, moduleName, outputDirectory);
  }

  private void generateModuleCodeForNeurons(
      final List<ASTNeuron> neurons,
      final String moduleName,
      final Path outputDirectory) {
    checkArgument(!neurons.isEmpty());

    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));
    setup.setTracing(false);

    final GlobalExtensionManagement glex = getGlexConfiguration();
    glex.setGlobalValue("neurons", neurons);
    glex.setGlobalValue("moduleName", moduleName);

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

    final Path initSLI = Paths.get( moduleName + "-init.sli");
    generator.generate(
        "org.nest.nestml.module.SLI_Init",
        initSLI,
        neurons.get(0)); // an arbitrary AST to match the signature

    info("Successfully generated NEST module code in " + outputDirectory, LOG_NAME);
  }

  private void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputFile) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputFile);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
      final String msg = "Cannot write the prettyprinted model to the file: " + outputFile;
      throw new RuntimeException(msg, e);
    }

  }

  private GlobalExtensionManagement getGlexConfiguration() {
    final GlobalExtensionManagement glex = new GlobalExtensionManagement();
    final NESTReferenceConverter converter = new NESTReferenceConverter();
    final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter(converter);

    final IReferenceConverter parameterBlockConverter = new NESTParameterBlockReferenceConverter();
    final ExpressionsPrettyPrinter parameterBlockPrinter = new ExpressionsPrettyPrinter(parameterBlockConverter);

    final IReferenceConverter stateBlockReferenceConverter = new NESTStateBlockReferenceConverter();
    final ExpressionsPrettyPrinter stateBlockPrettyPrinter = new ExpressionsPrettyPrinter(stateBlockReferenceConverter);

    glex.setGlobalValue("expressionsPrinter", expressionsPrinter);
    glex.setGlobalValue("functionCallConverter", converter);
    glex.setGlobalValue("idemPrinter", new ExpressionsPrettyPrinter());
    // this printer is used in one of the variable blocks. there, S_, V_, B_ structs are not defined and getters
    // setters must be used instead.
    glex.setGlobalValue("printerWithGetters", parameterBlockPrinter);
    glex.setGlobalValue("stateBlockPrettyPrinter", stateBlockPrettyPrinter);
    return glex;
  }


  private void setNeuronGenerationParameter(
      final GlobalExtensionManagement glex,
      final ASTNeuron neuron) {
    checkArgument(neuron.getSymbol().isPresent());
    defineSolverType(glex, neuron);

    final String guard = (neuron.getName()).replace(".", "_");
    glex.setGlobalValue("guard", guard);
    glex.setGlobalValue("simpleNeuronName", neuron.getName());
    glex.setGlobalValue("neuronSymbol", neuron.getSymbol().get());

    final NESTFunctionPrinter functionPrinter = new NESTFunctionPrinter();
    final ASTDeclarations declarations = new ASTDeclarations();
    glex.setGlobalValue("declarations", new ASTDeclarations() );
    glex.setGlobalValue("assignments", new ASTAssignments());
    glex.setGlobalValue("functionPrinter", functionPrinter);
    glex.setGlobalValue("functions", new SPLFunctionCalls());
    glex.setGlobalValue("declarations", declarations);
    glex.setGlobalValue("bufferHelper", new ASTBuffers());
    glex.setGlobalValue("variableHelper", new VariableHelper());
    glex.setGlobalValue("odeTransformer", new ODETransformer());

    glex.setGlobalValue("outputEvent", ASTOutputs.printOutputEvent(neuron.getBody()));
    glex.setGlobalValue("isOutputEventPresent", ASTOutputs.isOutputEventPresent(neuron.getBody()));
    glex.setGlobalValue("isSpikeInput", ASTInputs.isSpikeInput(neuron));
    glex.setGlobalValue("isCurrentInput", ASTInputs.isCurrentInput(neuron));
    glex.setGlobalValue("body", neuron.getBody());

    final GSLReferenceConverter converter = new GSLReferenceConverter();
    final ExpressionsPrettyPrinter expressionsPrinter = new ExpressionsPrettyPrinter(converter);
    glex.setGlobalValue("expressionsPrinterForGSL", expressionsPrinter);
    glex.setGlobalValue("nestmlSymbols", new NESTMLSymbols());
    glex.setGlobalValue("astUtils", new ASTUtils());
    glex.setGlobalValue("aliasInverter", new AliasInverter());

  }

  private void defineSolverType(final GlobalExtensionManagement glex, final ASTNeuron neuron) {
    final ASTBody astBody = neuron.getBody();
    glex.setGlobalValue("useGSL", false);
    if (astBody.getODEBlock().isPresent()) {
      if (astBody.getODEBlock().get().getShapes().size() == 0) {
        glex.setGlobalValue("useGSL", true);
        glex.setGlobalValue("ODEs", astBody.getODEBlock().get().getODEs());
      }

    }

  }

}
