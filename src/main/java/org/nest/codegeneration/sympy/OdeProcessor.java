/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.codegeneration.SolverType;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.reporting.Reporter;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.codegeneration.sympy.SolverFrameworkGenerator.generateODEAnalyserForDeltaShape;
import static org.nest.utils.AstUtils.deepCloneNeuron;
import static org.nest.utils.AstUtils.getFunctionCall;

/**
 * Analyzes a neuron for defined ODE. If an ode is defined, it produces a temporary NESTML model
 * with the exact solution if possible or creates an explicit form of the ODEs.
 *
 * @author plotnikov
 */
public class OdeProcessor {
  private final Reporter reporter = Reporter.get();
  private final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
  private final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
  private final ImplicitFormTransformer implicitFormTransformer = new ImplicitFormTransformer();
  private final DeltaSolutionTransformer deltaSolutionTransformer = new DeltaSolutionTransformer();

  /**
   * Dependent of the ODE kind either computes the exact solution or brings to the form which can
   * be directly utilized in a solver. The result is stored directly in the provided neuron AST.
   * @param astNeuron Input neuron.
   * @param outputBase Folder where the solverscript is generated  @return Exactly solved neuron.
   */
  public ASTNeuron solveODE(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final ASTBody astBody = astNeuron.getBody();
    if (astBody.getODEBlock().isPresent()) {
      reporter.reportProgress(String.format("The neuron %s contains an ODE block and will be analysed.", astNeuron.getName()));
      final Optional<ASTFunctionCall> deltaShape = getFunctionCall(
          PredefinedFunctions.DELTA, astBody.getODEBlock().get());

      if (deltaShape.isPresent()) {
        return handleDeltaShape(astNeuron, outputBase);
      }
      else {
        return handleNeuronWithODE(astNeuron, outputBase);
      }

    }
    reporter.reportProgress(String.format("The %s remains unchanged", astNeuron.getName()));
    return astNeuron;
  }

  private ASTNeuron handleDeltaShape(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final Optional<Path> generatedScript = generateODEAnalyserForDeltaShape(
        deepCloneNeuron(astNeuron, outputBase),
        outputBase);

    if(generatedScript.isPresent()) {
      reporter.reportProgress("The solver script is generated: " + generatedScript.get());

      boolean successfulExecution = false;//evaluator.solveOdeWithShapes(generatedScript.get());
      reporter.reportProgress("The solver script is evaluated. Results are under " + generatedScript.get().getParent());

      checkState(successfulExecution, "Error during solver script evaluation.");

      final Path odeTypePath = Paths.get(outputBase.toString(), astNeuron.getName() + "." + DeltaSolutionTransformer.SOLVER_TYPE);
      final SolverType solutionType = SolverType.fromFile(odeTypePath);

      if (solutionType.equals(SolverType.EXACT)) {
        reporter.reportProgress(astNeuron.getName() + " has a delta shape function with a linear ODE. " +
                                "It will be solved exactly.");
        deltaSolutionTransformer.addExactSolution(
            astNeuron,
            Paths.get(outputBase.toString(), astNeuron.getName() + "." + DeltaSolutionTransformer.P30_FILE),
            Paths.get(outputBase.toString(), astNeuron.getName() + "." + DeltaSolutionTransformer.PROPAGATOR_STEP));
      }
      else {
        reporter.reportProgress(astNeuron.getName() + " has a delta shape function with a non-linear ODE.");
      }

    }

    return astNeuron;
  }

  protected ASTNeuron handleNeuronWithODE(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final ASTNeuron deepCopy = deepCloneNeuron(astNeuron, outputBase);

    final SolverResult result = evaluator.solveOdeWithShapes(deepCopy.getBody().getODEBlock().get(), outputBase);
    reporter.reportProgress("The solver script is evaluated. Results are stored under " + outputBase.toString());


    if (result.solver.equals("exact")) {
      reporter.reportProgress("ODE is solved exactly.");

      return linearSolutionTransformer.addExactSolution(
          astNeuron,
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.P30_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.PSC_INITIAL_VALUE_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VARIABLES_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.PROPAGATOR_MATRIX_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.PROPAGATOR_STEP_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VECTOR_TMP_DECLARATIONS_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VECTOR_UPDATE_STEPS_FILE),
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VECTOR_TMP_BACK_ASSIGNMENTS_FILE));
    }
    else if (result.solver.equals("numeric")) {
      reporter.reportProgress("ODE is solved numerically.");

      return implicitFormTransformer.transformToImplicitForm(
          astNeuron,
          Paths.get(outputBase.toString(), astNeuron.getName() + "." + ImplicitFormTransformer.PSC_INITIAL_VALUE_FILE),
          Paths.get(outputBase.toString(),astNeuron.getName() + "." + ImplicitFormTransformer.EQUATIONS_FILE));
    }
    else {
      reporter.reportProgress(astNeuron.getName() + ": ODEs could not be solved. The model remains unchanged.");
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
