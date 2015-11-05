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
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.utils.ASTNodes;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static de.se_rwth.commons.Names.getPathFromPackage;
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
   * @param astNestmlCompilationUnit Model root
   * @param neuron Neuron from the nestml model (must be part of the root)
   * @param outputDirectory Base directory for the output
   * @return Path to the generated script of @code{empty()} if there is no ODE definition.
   */
  public static Optional<Path> generateSympyODEAnalyzer(
      final ASTNESTMLCompilationUnit astNestmlCompilationUnit,
      final ASTNeuron neuron,
      final File outputDirectory) {
    final GeneratorSetup setup = new GeneratorSetup(outputDirectory);

    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(neuron.getBody());
    final Optional<ASTOdeDeclaration> odeDefinition = astBodyDecorator.getOdeDefinition();

    if (odeDefinition.isPresent()) {
      final Path generatedScriptFile = generateSolverScript(
          createGLEXConfiguration(),
          astNestmlCompilationUnit,
          neuron,
          odeDefinition.get(),
          setup);

      final String msg = String.format(
          "Successfully generated solver script for neuron %s under %s",
          neuron.getName(),
          generatedScriptFile.toString());
      Log.info(msg, LOG_NAME);

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
      final ASTNESTMLCompilationUnit compilationUnit,
      final ASTNeuron neuron,
      final ASTOdeDeclaration astOdeDeclaration,
      final GeneratorSetup setup) {
    final String fullName = Names.getQualifiedName(compilationUnit.getPackageName().getParts());

    final ExpressionsPrettyPrinter expressionsPrettyPrinter = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("ode", astOdeDeclaration.getODEs());
    glex.setGlobalValue("eq", astOdeDeclaration.getEq());
    glex.setGlobalValue("expressionsPrettyPrinter", expressionsPrettyPrinter);

    setup.setGlex(glex);
    setup.setTracing(false); // python comments are not java comments

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverFile= Paths.get(getPathFromPackage(fullName), neuron.getName() + "Solver.py");

    // TODO: filter out E
    final List<String> variables = filterConstantVariables(
        ASTNodes.getVariablesNamesFromAst(astOdeDeclaration));
    glex.setGlobalValue("variables", variables);

    // TODO: how do I find out the call was successful?
    generator.generate(
        "org.nest.codegeneration.sympy.SympySolver",
        solverFile,
        astOdeDeclaration);
    

    return Paths.get(setup.getOutputDirectory().getPath(), solverFile.toString());
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

