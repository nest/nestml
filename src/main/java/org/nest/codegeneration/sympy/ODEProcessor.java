/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.SolverType;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.codegeneration.sympy.ODESolverScriptGenerator.generateSympyODEAnalyzer;

/**
 * Analyzes a neuron for defined ODE. If an ode is defined, it produces a temporary NESTML model
 * with the exact solution if possible or creates an explicit form of the ODEs.
 *
 * @author plotnikov
 */
public class ODEProcessor {
  private final String LOG_NAME = ODEProcessor.class.getName();

  private final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();

  /**
   * Dependent of the ODE kind either computes the exact solution or brings to the form which can
   * be directly utilized in a solver. The result is stored directly in the provided neuron AST.
   * @param astNeuron Input neuron.
   * @param outputBase Folder where the solverscript is generated
   * @return Exactly solved neuron.
   */
  public ASTNeuron solveODE(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final ASTBody astBody = astNeuron.getBody();
    if (astBody.getEquations().isPresent()) {
      return handleNeuronWithODE(astNeuron, outputBase);
    }
    else {
      final String msg = "The neuron: " + astNeuron.getName() + " doesn't contain ODE. "
          + "The analysis is skipped.";
      Log.warn(msg);
      return astNeuron;
    }

  }

  protected ASTNeuron handleNeuronWithODE(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final Optional<Path> generatedScript = generateSympyODEAnalyzer(astNeuron, outputBase);
    checkState(generatedScript.isPresent());
    info("The solver script is generated: " + generatedScript.get(), LOG_NAME);

    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
    boolean successfulExecution = evaluator.execute(generatedScript.get());
    info("The solver script is evaluated. Results are under " + generatedScript.get().getParent(), LOG_NAME);

    checkState(successfulExecution, "Error during solver script evaluation.");

    final Path odeTypePath = Paths.get(outputBase.toString(), SymPyScriptEvaluator.ODE_TYPE);
    final SolverType solutionType = SolverType.fromFile(odeTypePath);

    if (solutionType.equals(SolverType.EXACT)) {
      info("ODE is solved exactly.", LOG_NAME);

      return exactSolutionTransformer
          .replaceODEWithSymPySolution(
              astNeuron,
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.P30_FILE),
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE),
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.STATE_VECTOR_FILE),
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.UPDATE_STEP_FILE));
    }
    else if (solutionType.equals(SolverType.NUMERIC)) {
      info("ODE is solved numerically.", LOG_NAME);
      return astNeuron;
    }
    else {
      warn("ODEs could not be solved. The model remains unchanged.");
      return astNeuron;
    }

  }

  public ExactSolutionTransformer getExactSolutionTransformer() {
    return exactSolutionTransformer;
  }
}
