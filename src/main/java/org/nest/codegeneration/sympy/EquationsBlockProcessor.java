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
import org.nest.reporting.Reporter;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.codegeneration.sympy.SolverFrameworkGenerator.generateODEAnalyserForDeltaShape;
import static org.nest.nestml._symboltable.predefined.PredefinedFunctions.*;
import static org.nest.utils.AstUtils.deepCloneNeuronAndBuildSymbolTable;
import static org.nest.utils.AstUtils.getFunctionCall;

/**
 * Analyzes a neuron for defined ODE. If an ode is defined, it produces a temporary NESTML model
 * with the exact solution if possible or creates an explicit form of the ODEs.
 *
 * @author plotnikov
 */
public class EquationsBlockProcessor {
  private final Reporter reporter = Reporter.get();
  private final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
  private final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
  private final ShapesToOdesTransformer shapesToOdesTransformer = new ShapesToOdesTransformer();
  private final DeltaSolutionTransformer deltaSolutionTransformer = new DeltaSolutionTransformer();

  /**
   * Dependent of the ODE kind either computes the exact solution or brings to the form which can
   * be directly utilized in a solver. The result is stored directly in the provided neuron AST.
   * @param astNeuron Input neuron.
   * @param outputBase Folder where the solverscript is generated
   * @return Transformed neuron with either: exact solution or transformed shapes to its ODE notation
   */
  public ASTNeuron solveOdeWithShapes(final ASTNeuron astNeuron, final Path outputBase) {
    final ASTBody astBody = astNeuron.getBody();
    if (astBody.getOdeBlock().isPresent()) {

      reporter.reportProgress(String.format("The neuron %s contains an ODE block. It will be analysed.", astNeuron.getName()));
      final Optional<ASTFunctionCall> deltaShape = getFunctionCall(DELTA, astBody.getOdeBlock().get());

      if (deltaShape.isPresent()) {
        return handleDeltaShape(astNeuron, outputBase);
      }
      else {
        return handleNonDeltaShapes(astNeuron, outputBase);
      }

    }
    reporter.reportProgress(String.format("The %s remains unchanged", astNeuron.getName()));
    return astNeuron;
  }

  private ASTNeuron handleDeltaShape(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final Optional<Path> generatedScript = generateODEAnalyserForDeltaShape(
        deepCloneNeuronAndBuildSymbolTable(astNeuron, outputBase),
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

  ASTNeuron handleNonDeltaShapes(
      final ASTNeuron astNeuron,
      final Path outputBase) {
    final ASTNeuron deepCopy = deepCloneNeuronAndBuildSymbolTable(astNeuron, outputBase);
    // this function is called only for neurons with an ode block. thus, retrieving it is safe.
    if (deepCopy.getBody().getOdeBlock().get().getShapes().size() > 0 &&
        deepCopy.getBody().getOdeBlock().get().getODEs().size() > 1) {
      reporter.reportProgress("Shapes will be solved with GLS.");
      final SolverOutput solverOutput = evaluator.solveShapes(deepCopy.getBody().getOdeBlock().get().getShapes(), outputBase);
      return shapesToOdesTransformer.transformShapesToOdeForm(solverOutput, astNeuron);
    }
    else {
      final SolverOutput solverOutput = evaluator.solveOdeWithShapes(deepCopy.getBody().getOdeBlock().get(), outputBase);
      reporter.reportProgress("The model ODE with shapes will be analyzed.");
      reporter.reportProgress("The solver script is evaluated. Results are stored under " + outputBase.toString());

      switch (solverOutput.solver) {
        case "exact":
          reporter.reportProgress("Equations are solved exactly.");
          return exactSolutionTransformer.addExactSolution(astNeuron, solverOutput);

        case "numeric":
          reporter.reportProgress("Shapes will be solved with GLS.");
          return shapesToOdesTransformer.transformShapesToOdeForm(solverOutput, astNeuron);

        default:
          reporter.reportProgress(astNeuron.getName() +
                                  ": Equations or shapes could not be solved. The model remains unchanged.");
          return astNeuron;
      }

    }

  }

}
