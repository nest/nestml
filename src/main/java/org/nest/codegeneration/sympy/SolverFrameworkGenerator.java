/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTOdeDeclaration;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.nestml._symboltable.predefined.PredefinedVariables;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static java.util.Optional.empty;
import static java.util.Optional.of;
import static org.nest.utils.AstUtils.getVariableSymbols;

/**
 * Wrapps the logic how to extract and generate SymPy script.
 *
 * @author plotnikov
 */
@Deprecated
public class SolverFrameworkGenerator {
  private final static String LOG_NAME = SolverFrameworkGenerator.class.getName();
  private static final String SHAPES_SCRIPT = "shapes.py";
  private static final String SHAPES_SCRIPT_SOURCE = "org/nest/sympy/shapes.py";
  private static final String DELTA_SHAPE_SOLVER_GENERATOR_TEMPLATE = "org.nest.sympy.DeltaShapeSolver";


  /**
   * Runs code generation for the sympy script to solve an arbitrary ODE
   *
   * @param neuron Neuron from the nestml model (must be part of the root)
   * @param outputDirectory Base directory for the output
   * @return Path to the generated script of @code{empty()} if there is no ODE definition.
   */
  static Optional<Path> generateODEAnalyserForDeltaShape(
      final ASTNeuron neuron,
      final Path outputDirectory) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));

    final ASTBody astBodyDecorator = (neuron.getBody());
    final Optional<ASTOdeDeclaration> odeDefinition = astBodyDecorator.getODEBlock();

    if (odeDefinition.isPresent()) {
      final Path generatedScriptFile = generateDeltaScript(
          createGLEXConfiguration(),
          neuron,
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
      Log.trace(msg, LOG_NAME);

      return empty();
    }

  }

  static Path generateDeltaScript(
      final GlobalExtensionManagement glex,
      final ASTNeuron neuron,
      final String templateName,
      final ASTOdeDeclaration astOdeDeclaration,
      final GeneratorSetup setup) {
    checkArgument(neuron.getEnclosingScope().isPresent(), "Run symboltable creator");
    final Scope scope = astOdeDeclaration.getEnclosingScope().get();

    if (astOdeDeclaration.getODEs().size() >= 1) {
      Log.trace("It works only for a single ODE. Only the first equation will be used.", LOG_NAME);
    }

    glex.setGlobalValue("ode", astOdeDeclaration.getODEs().get(0));
    glex.setGlobalValue("shapes", astOdeDeclaration.getShapes());


    glex.setGlobalValue("predefinedVariables", PredefinedVariables.gerVariables());

    setup.setGlex(glex);
    setup.setCommentStart(Optional.of("#"));
    setup.setCommentEnd(Optional.empty());

    final Set<VariableSymbol> variables = new HashSet<>(getVariableSymbols(astOdeDeclaration));
    final List<VariableSymbol> aliases =  astOdeDeclaration.getOdeFunctions()
        .stream()
        .map(alias -> VariableSymbol.resolve(alias.getVariableName(), scope))
        .collect(Collectors.toList());

    for (final ASTEquation ode:astOdeDeclaration.getODEs()) {
      final VariableSymbol lhsSymbol = VariableSymbol.resolve(AstUtils.getNameOfLHS(ode.getLhs()), scope);
      variables.add(lhsSymbol);
    }

    glex.setGlobalValue("variables", variables);
    glex.setGlobalValue("aliases", aliases);
    glex.setGlobalValue("neuronName", neuron.getName());

    final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("printer", expressionsPrinter);
    glex.setGlobalValue("odeTransformer", new OdeTransformer());

    final GeneratorEngine generator = new GeneratorEngine(setup);
    final Path solverSubPath = Paths.get( neuron.getName() + "Solver.py");
    generator.generate(templateName, solverSubPath, astOdeDeclaration);

    return solverSubPath;
  }

  public static String generateExactSolverCommand(final ASTNeuron neuron) {
    checkArgument(neuron.getEnclosingScope().isPresent(), "Run symboltable creator");
    checkArgument(neuron.getBody().getODEBlock().isPresent(), "Supports only ODEs with an ODE block.");
    final ASTOdeDeclaration astOdeDeclaration = neuron.getBody().getODEBlock().get();
    checkArgument(astOdeDeclaration.getODEs().size() == 1 && astOdeDeclaration.getODEs().size() > 0,
                  "Exact solver supports only a single ode with at least one shape!");

    final Scope scope = astOdeDeclaration.getEnclosingScope().get();
    final ClassLoader classloader = SolverFrameworkGenerator.class.getClassLoader();
    astOdeDeclaration.getODEs().forEach(SolverFrameworkGenerator::simplifySums);

    try {
      final URL solverScript = classloader.getResource(SHAPES_SCRIPT_SOURCE);
      checkNotNull(solverScript, "Cannot read the solver script: " + SHAPES_SCRIPT_SOURCE);
      final String shapes_py = Resources.toString(solverScript, Charsets.UTF_8);
      return String.format("echo %s > shapes.py | python shapes.py", shapes_py);
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }

  }

  private static ASTEquation simplifySums(final ASTEquation astEquation) {
    ASTEquation tmp = OdeTransformer.replaceSumCalls(astEquation);
    astEquation.setRhs(tmp.getRhs());
    return astEquation;
  }

  private static GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}

