/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.ast.ASTNode;
import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static java.util.Optional.empty;
import static java.util.Optional.of;
import static java.util.stream.Collectors.toList;
import static org.nest.symboltable.predefined.PredefinedFunctions.I_SUM;
import static org.nest.utils.ASTUtils.getVariableSymbols;

/**
 * Wrapps the logic how to extract and generate SymPy script..
 * @author plotnikov
 */
public class SympyScriptGenerator {

  private final static String LOG_NAME = SympyScriptGenerator.class.getName();

  private static final String ODE_SOLVER_GENERATOR_TEMPLATE = "org.nest.sympy.ODESolver";
  private static final String DELTA_SHAPE_SOLVER_GENERATOR_TEMPLATE = "org.nest.sympy.DeltaShapeSolver";

  /**
   * Runs code generation for the sympy script to solve an arbitrary ODE
   *
   * @param neuron Neuron from the nestml model (must be part of the root)
   * @param outputDirectory Base directory for the output
   * @return Path to the generated script of @code{empty()} if there is no ODE definition.
   */
  public static Optional<Path> generateSympyODEAnalyzer(
      final ASTNeuron neuron,
      final Path outputDirectory) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));

    final ASTBody astBodyDecorator = (neuron.getBody());
    final Optional<ASTOdeDeclaration> odeDefinition = astBodyDecorator.getEquations();

    if (odeDefinition.isPresent()) {
      final Path generatedScriptFile = generateSympyScript(
          createGLEXConfiguration(),
          neuron.deepClone(), // is necessary because the model is altered inplace, e.g replacing I_sum(Buffer, Shape)
          ODE_SOLVER_GENERATOR_TEMPLATE,
          odeDefinition.get(),
          setup);

      final String msg = String.format(
          "Successfully generated solver script for neuron %s under %s",
          neuron.getName(),
          generatedScriptFile.toString());
      info(msg, LOG_NAME);

      return of(generatedScriptFile);
    }
    else {
      final String msg = String.format("The neuron %s doesn't contain an ODE. The script generation "
          + "is skipped.", neuron.getName());
      Log.warn(msg);

      return empty();
    }

  }

  /**
   * Runs code generation for the sympy script to solve an arbitrary ODE
   *
   * @param neuron Neuron from the nestml model (must be part of the root)
   * @param outputDirectory Base directory for the output
   * @return Path to the generated script of @code{empty()} if there is no ODE definition.
   */
  public static Optional<Path> generateODEAnalyserForDeltaShape(
      final ASTNeuron neuron,
      final Path outputDirectory) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));

    final ASTBody astBodyDecorator = (neuron.getBody());
    final Optional<ASTOdeDeclaration> odeDefinition = astBodyDecorator.getEquations();

    if (odeDefinition.isPresent()) {
      final Path generatedScriptFile = generateSympyScript(
          createGLEXConfiguration(),
          neuron.deepClone(), // is necessary because the model is altered inplace, e.g replacing I_sum(Buffer, Shape)
          DELTA_SHAPE_SOLVER_GENERATOR_TEMPLATE,
          odeDefinition.get(),
          setup);

      final String msg = String.format(
          "Successfully generated solver script for neuron %s under %s",
          neuron.getName(),
          generatedScriptFile.toString());
      info(msg, LOG_NAME);

      return of(generatedScriptFile);
    }
    else {
      final String msg = String.format("The neuron %s doesn't contain an ODE. The script generation "
          + "is skipped.", neuron.getName());
      Log.warn(msg);

      return empty();
    }

  }

  private static Path generateSympyScript(
      final GlobalExtensionManagement glex,
      final ASTNeuron neuron,
      final String templateName,
      final ASTOdeDeclaration astOdeDeclaration,
      final GeneratorSetup setup) {
    checkArgument(neuron.getEnclosingScope().isPresent(), "Run symboltable creator");
    if (astOdeDeclaration.getODEs().size() >= 1) {
      Log.warn("It works only for a single ODE. Only the first equation will be used.");
    }

    final ASTEquation workingVersion = replace_I_sum(astOdeDeclaration.getODEs().get(0));

    glex.setGlobalValue("ode", workingVersion);
    glex.setGlobalValue("EQs", astOdeDeclaration.getShapes());
    glex.setGlobalValue("predefinedVariables", PredefinedVariables.gerVariables());

    setup.setGlex(glex);
    setup.setCommentStart(Optional.of("#"));
    setup.setCommentEnd(Optional.empty());

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverSubPath = Paths.get( neuron.getName() + "Solver.py");

    final Set<VariableSymbol> variables = new HashSet<>(getVariableSymbols(astOdeDeclaration));

    final List<VariableSymbol> aliases = ASTUtils.getAliasSymbols(astOdeDeclaration);

    List<VariableSymbol> symbolsInAliasDeclaration = aliases
        .stream()
        .flatMap(alias -> getVariableSymbols(alias.getDeclaringExpression().get()).stream())
        .collect(Collectors.toList());
    variables.addAll(symbolsInAliasDeclaration);

    final Scope scope = astOdeDeclaration.getEnclosingScope().get();

    for (final ASTEquation ode:astOdeDeclaration.getODEs()) {
      final VariableSymbol lhsSymbol = VariableSymbol.resolve(ode.getLhs().toString(), scope);
      variables.add(lhsSymbol);
    }

    glex.setGlobalValue("variables", variables);
    glex.setGlobalValue("aliases", aliases);

    final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("printer", expressionsPrinter);

    generator.generate(templateName, solverSubPath, astOdeDeclaration);

    return Paths.get(setup.getOutputDirectory().getPath(), solverSubPath.toString());
  }

  static ASTEquation replace_I_sum(final ASTEquation astOde) {
    final List<ASTFunctionCall> functions = ASTUtils.getAll(astOde, ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(I_SUM))
        .collect(toList());

    functions.stream().forEach(node -> replaceFunctionCallThroughFirstArgument(astOde, node));
    return astOde;
  }

  private static void replaceFunctionCallThroughFirstArgument(ASTEquation astOde, ASTFunctionCall node) {
    final Optional<ASTNode> parent = ASTUtils.getParent(node, astOde);
    checkState(parent.isPresent());
    final ASTExpr expr = (ASTExpr) parent.get();
    expr.setFunctionCall(null);
    expr.setVariable(node.getArgs().get(0).getVariable().get());
  }


  private static GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}

