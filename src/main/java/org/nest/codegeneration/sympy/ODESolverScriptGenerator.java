/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.converters.IReferenceConverter;
import org.nest.codegeneration.converters.IdempotentReferenceConverter;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static java.util.Optional.empty;
import static java.util.Optional.of;

/**
 * Wrapps the logic how to extract and generate SymPy script..
 * @author plotnikov
 */
public class ODESolverScriptGenerator {

  private final static String LOG_NAME = ODESolverScriptGenerator.class.getName();

  public static final String SCRIPT_GENERATOR_TEMPLATE = "org.nest.sympy.SympySolver";

  /**
   * Runs code generation for the codegeneration.sympy script, if the particular neuron contains an ODE definition.
   * @param neuron Neuron from the nestml model (must be part of the root)
   * @param outputDirectory Base directory for the output
   * @return Path to the generated script of @code{empty()} if there is no ODE definition.
   */
  public static Optional<Path> generateSympyODEAnalyzer(
      final ASTNeuron neuron,
      final Path outputDirectory) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));

    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(neuron.getBody());
    final Optional<ASTOdeDeclaration> odeDefinition = astBodyDecorator.getEquations();

    if (odeDefinition.isPresent()) {
      final Path generatedScriptFile = generateSolverScript(
          createGLEXConfiguration(),
          neuron,
          odeDefinition.get(),
          setup);

      final String msg = String.format(
          "Successfully generated solver script for neuron %s under %s",
          neuron.getName(),
          generatedScriptFile.toString());
      info(msg, LOG_NAME);

      return of(generatedScriptFile);
    }

    final String msg = String.format("The neuron %s doesn't contain an ODE. The script generation "
        + "is skipped.", neuron.getName());
    Log.warn(msg);

    return empty();
  }

  private static Path generateSolverScript(
      final GlobalExtensionManagement glex,
      final ASTNeuron neuron,
      final ASTOdeDeclaration astOdeDeclaration,
      final GeneratorSetup setup) {

    final ExpressionsPrettyPrinter expressionsPrettyPrinter = new ExpressionsPrettyPrinter();
    checkState(astOdeDeclaration.getODEs().size() == 1, "It works only for a single ODE.");
    glex.setGlobalValue("ode", astOdeDeclaration.getODEs().get(0));
    glex.setGlobalValue("EQs", astOdeDeclaration.getEqs());
    // TODO should be defined in sympy fileglex.setGlobalValue("predefinedVariables", PredefinedVariables.gerVariables());

    setup.setGlex(glex);
    setup.setTracing(false); // python comments are not java comments
    setup.setCommentStart(Optional.of("#"));
    setup.setCommentEnd(Optional.empty());

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverSubPath = Paths.get( neuron.getName() + "Solver.py");

    final List<VariableSymbol> variables = ASTNodes.getVariableSymbols(astOdeDeclaration);
    final List<VariableSymbol> aliases = variables.stream()
        .filter(VariableSymbol::isAlias)
        .collect(Collectors.toList());
    aliases.stream().forEach(alias ->
        variables.addAll(ASTNodes.getVariableSymbols(alias.getDeclaringExpression().get())));

    glex.setGlobalValue("variables", variables);
    glex.setGlobalValue("aliases", aliases);

    final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("expressionsPrinter", expressionsPrinter);

    generator.generate(SCRIPT_GENERATOR_TEMPLATE, solverSubPath, astOdeDeclaration);

    return Paths.get(setup.getOutputDirectory().getPath(), solverSubPath.toString());
  }

  private static GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}

