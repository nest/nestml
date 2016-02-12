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
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._ast.ASTFunctionCall;
import org.nest.spl._ast.ASTODE;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.predefined.PredefinedVariables;
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
import static java.util.stream.Collectors.toList;
import static org.nest.utils.ASTNodes.getVariableSymbols;

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

    final ASTBody astBodyDecorator = (neuron.getBody());
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

    checkState(astOdeDeclaration.getODEs().size() == 1, "It works only for a single ODE.");
    glex.setGlobalValue("ode", replace_I_sum(astOdeDeclaration.getODEs().get(0)));
    glex.setGlobalValue("EQs", astOdeDeclaration.getEqs());
    glex.setGlobalValue("predefinedVariables", PredefinedVariables.gerVariables());

    setup.setGlex(glex);
    setup.setCommentStart(Optional.of("#"));
    setup.setCommentEnd(Optional.empty());

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverSubPath = Paths.get( neuron.getName() + "Solver.py");

    final List<VariableSymbol> variables = getVariableSymbols(astOdeDeclaration);
    final List<VariableSymbol> aliases = variables.stream()
        .filter(VariableSymbol::isAlias)
        .collect(toList());
    aliases.stream()
        .forEach(alias -> variables.addAll(getVariableSymbols(alias.getDeclaringExpression().get())));

    glex.setGlobalValue("variables", variables);
    glex.setGlobalValue("aliases", aliases);

    final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("printer", expressionsPrinter);

    generator.generate(SCRIPT_GENERATOR_TEMPLATE, solverSubPath, astOdeDeclaration);

    return Paths.get(setup.getOutputDirectory().getPath(), solverSubPath.toString());
  }

  protected static ASTODE replace_I_sum(final ASTODE astOde) {
    final List<ASTFunctionCall> functions = ASTNodes.getAll(astOde, ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals("I_sum"))
        .collect(toList());

    functions.stream().forEach(node -> {
      final Optional<ASTNode> parent = ASTNodes.getParent(node, astOde);
      checkState(parent.isPresent());
      final ASTExpr expr = (ASTExpr) parent.get();
      expr.setFunctionCall(null);
      expr.setVariable(node.getArgList().getArgs().get(0).getVariable().get());
    });
    return astOde;
  }

  private static GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}

