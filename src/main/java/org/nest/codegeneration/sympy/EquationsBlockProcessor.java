/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.reporting.Reporter;

import java.nio.file.Path;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.nestml._symboltable.predefined.PredefinedFunctions.DELTA;
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
  private final SymPySolver evaluator = new SymPySolver();
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
    if (astNeuron.getOdeBlock().isPresent()) {
      reporter.reportProgress(String.format("The neuron %s contains an ODE block. It will be analysed.", astNeuron.getName()));

      final ASTNeuron deepCopy = deepCloneNeuronAndBuildSymbolTable(astNeuron, outputBase);
      // this function is called only for neurons with an ode block. thus, retrieving it is safe.
      if (deepCopy.getOdeBlock().get().getShapes().size() > 0 &&
          deepCopy.getOdeBlock().get().getODEs().size() == 1) {

        final SolverOutput solverOutput = evaluator.solveOdeWithShapes(deepCopy.getOdeBlock().get(), outputBase);
        reporter.reportProgress("The model ODE with shapes will be analyzed.");
        reporter.reportProgress("The solver script is evaluated. Results are stored under " + outputBase.toString());

        if (!solverOutput.status.equals("success")) {
          reporter.reportProgress(astNeuron.getName() +
                                  ": Equations or shapes could not be solved. The model remains unchanged.");
          return astNeuron;
        }

        switch (solverOutput.solver) {
          case "exact":
            reporter.reportProgress("Equations are solved exactly.");
            return exactSolutionTransformer.addExactSolution(astNeuron, solverOutput);

          case "numeric":
            reporter.reportProgress("Shapes will be solved with GLS.");
            return shapesToOdesTransformer.transformShapesToOdeForm(astNeuron, solverOutput);
          case "delta":
            return deltaSolutionTransformer.addExactSolution(solverOutput, astNeuron);
          default:
            reporter.reportProgress(astNeuron.getName() +
                                    ": Equations or shapes could not be solved. The model remains unchanged.");
            return astNeuron;
        }
      }
      else if (deepCopy.getOdeBlock().get().getShapes().size() > 0) {
        reporter.reportProgress("Shapes will be solved with GLS.");
        final SolverOutput solverOutput = evaluator.solveShapes(deepCopy.getOdeBlock().get().getShapes(), outputBase);
        return shapesToOdesTransformer.transformShapesToOdeForm(astNeuron, solverOutput);

      }

    }
    reporter.reportProgress(String.format("The %s remains unchanged", astNeuron.getName()));
    return astNeuron;
  }

}
