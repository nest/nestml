/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.SolverType;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.symboltable.predefined.PredefinedFunctions;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.codegeneration.sympy.ODESolverGenerator.generateODEAnalyserForDeltaShape;
import static org.nest.codegeneration.sympy.ODESolverGenerator.generateSympyODEAnalyzer;
import static org.nest.utils.ASTUtils.getFunctionCall;

/**
 * Analyzes a neuron for defined ODE. If an ode is defined, it produces a temporary NESTML model
 * with the exact solution if possible or creates an explicit form of the ODEs.
 *
 * @author plotnikov
 */
public class ODEProcessor {
  private final String LOG_NAME = ODEProcessor.class.getName();

  private final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
  private final ImplicitFormTransformer implicitFormTransformer = new ImplicitFormTransformer();
  private final DeltaSolutionTransformer deltaSolutionTransformer = new DeltaSolutionTransformer();

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
    if (astBody.getODEBlock().isPresent()) {
      final Optional<ASTFunctionCall> deltaShape = getFunctionCall(
          PredefinedFunctions.DELTA,
          astBody.getODEBlock().get());

      if (deltaShape.isPresent()) {
        return handleDeltaShape(astNeuron, outputBase);
      }
      else {
        return handleNeuronWithODE(astNeuron, outputBase);
      }

    }
    else {
      final String msg = "The neuron: " + astNeuron.getName() + " doesn't contain ODE. "
          + "The analysis is skipped.";
      Log.warn(msg);
      return astNeuron;
    }

  }

  private ASTNeuron handleDeltaShape(final ASTNeuron astNeuron, final Path outputBase) {
    final Optional<Path> generatedScript = generateODEAnalyserForDeltaShape(astNeuron.deepClone(), outputBase);
    if(generatedScript.isPresent()) {
      info("The solver script is generated: " + generatedScript.get(), LOG_NAME);

      final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
      boolean successfulExecution = evaluator.evaluateScript(generatedScript.get());
      info("The solver script is evaluated. Results are under " + generatedScript.get().getParent(), LOG_NAME);

      checkState(successfulExecution, "Error during solver script evaluation.");

      final Path odeTypePath = Paths.get(outputBase.toString(), DeltaSolutionTransformer.ODE_TYPE);
      final SolverType solutionType = SolverType.fromFile(odeTypePath);

      if (solutionType.equals(SolverType.EXACT)) {
        Log.info(
            astNeuron.getName() + " has a delta shape function with a linear ODE. It will be solved exactly.",
            LOG_NAME);
        deltaSolutionTransformer.addExactSolution(
            astNeuron,
            Paths.get(outputBase.toString(), DeltaSolutionTransformer.P30_FILE),
            Paths.get(outputBase.toString(), DeltaSolutionTransformer.PROPAGATOR_STEP));
      }
      else {
        Log.warn(astNeuron.getName() + " has a delta shape function with a non-linear ODE.");
      }
    }

    return astNeuron;
  }

  protected ASTNeuron handleNeuronWithODE(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final Optional<Path> generatedScript = generateSympyODEAnalyzer(astNeuron.deepClone(), outputBase);
    if(generatedScript.isPresent()) {
      info("The solver script is generated: " + generatedScript.get(), LOG_NAME);

      final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
      boolean successfulExecution = evaluator.evaluateScript(generatedScript.get());
      info("The solver script is evaluated. Results are stored under " + generatedScript.get().getParent(), LOG_NAME);

      checkState(successfulExecution, "Error during solver script evaluation.");

      final Path odeTypePath = Paths.get(outputBase.toString(), TransformerBase.SOLVER_TYPE);
      final SolverType solutionType = SolverType.fromFile(odeTypePath);

      if (solutionType.equals(SolverType.EXACT)) {
        info("ODE is solved exactly.", LOG_NAME);

        return linearSolutionTransformer
            .addExactSolution(
                astNeuron,
                Paths.get(outputBase.toString(), LinearSolutionTransformer.P30_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.PSC_INITIAL_VALUE_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.STATE_VARIABLES_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.PROPAGATOR_MATRIX_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.PROPAGATOR_STEP_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.STATE_VECTOR_TMP_DECLARATIONS_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.STATE_VECTOR_UPDATE_STEPS_FILE),
                Paths.get(outputBase.toString(), LinearSolutionTransformer.STATE_VECTOR_TMP_BACK_ASSIGNMENTS_FILE));
      }
      else if (solutionType.equals(SolverType.NUMERIC)) {
        info("ODE is solved numerically.", LOG_NAME);
        return implicitFormTransformer.transformToImplicitForm(
            astNeuron,
            Paths.get(outputBase.toString(),ImplicitFormTransformer.PSC_INITIAL_VALUE_FILE),
            Paths.get(outputBase.toString(),ImplicitFormTransformer.EQUATIONS_FILE));
      }
      else {
        warn(astNeuron.getName() + ": ODEs could not be solved. The model remains unchanged.");
        return astNeuron;
      }
    }
    else {
      warn(astNeuron.getName() + ": ODEs could not be solved. The model remains unchanged.");
      return astNeuron;
    }

  }

  /**
   * This method can be overloaded in tests and return a mock instead of real transformer.
   */
  protected LinearSolutionTransformer getLinearSolutionTransformer() {
    return linearSolutionTransformer;
  }

  /**
   * This method can be overloaded in tests and return a mock instead of real transformer.
   */
  protected ImplicitFormTransformer getImplicitFormTransformer() {
    return implicitFormTransformer;
  }

}
