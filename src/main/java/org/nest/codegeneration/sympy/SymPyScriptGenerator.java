/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
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
public class SymPyScriptGenerator {
  private final static String LOG_NAME = SymPyScriptGenerator.class.getName();
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
    final Optional<ASTOdeDeclaration> odeDefinition = astBodyDecorator.getOdeDefinition();

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

    final String msg = String.format(
        "The neuron %s doesn't contain an ODE. The script generation is skipped.",
        neuron.getName());
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
    glex.setGlobalValue("expressionsPrettyPrinter", expressionsPrettyPrinter);

    setup.setGlex(glex);
    setup.setTracing(false); // python comments are not java comments

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverSubPath = Paths.get( neuron.getName() + "Solver.py");

    // TODO: filter out E
    final List<String> variables = filterConstantVariables(
        ASTNodes.getVariablesNamesFromAst(astOdeDeclaration));
    glex.setGlobalValue("variables", variables);

    // TODO: how do I find out the call was successful?
    generator.generate(
        "org.nest.sympy.SympySolver",
        solverSubPath,
        astOdeDeclaration);

    return Paths.get(setup.getOutputDirectory().getPath(), solverSubPath.toString());
  }

  /**
   * Filters mathematical constants like Pi, E, ...
   */
  private static List<String> filterConstantVariables(final List<String> variablesNames) {
    final List<String> result = Lists.newArrayList();
    result.addAll(variablesNames.stream().filter(variable -> !variable.equals("E"))
        .collect(Collectors.toList()));

    return result;
  }

  private static GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}

