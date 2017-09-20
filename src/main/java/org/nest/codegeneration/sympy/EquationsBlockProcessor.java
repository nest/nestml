/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTShape;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.reporting.Reporter;

import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

import static org.nest.codegeneration.sympy.TransformerBase.applyIncomingSpikes;
import static org.nest.utils.AstUtils.deepCloneNeuronAndBuildSymbolTable;

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
    ASTNeuron workingVersion = astNeuron;
    if (workingVersion.findEquationsBlock().isPresent()) {
      reporter.reportProgress(String.format("The neuron %s contains an ODE block. It will be analysed.", astNeuron.getName()));

      final ASTNeuron deepCopy = deepCloneNeuronAndBuildSymbolTable(workingVersion, outputBase);
      // this function is called only for neurons with an ode block. thus, retrieving it is safe.
      if (workingVersion.findEquationsBlock().get().getShapes().size() > 0 &&
          !odeShapeExists(workingVersion.findEquationsBlock().get().getShapes()) &&
          workingVersion.findEquationsBlock().get().getEquations().size() == 1) {

        // this uses the copy of the AST since the python generator changes the AST during the generation
        final SolverOutput solverOutput = evaluator.solveOdeWithShapes(deepCopy.findEquationsBlock().get(), outputBase);
        reporter.reportProgress("The model ODE with shapes will be analyzed.");
        reporter.reportProgress("The solver script is evaluated. Results are stored under " + outputBase.toString());

        if (!solverOutput.status.equals("success")) {
          reporter.reportProgress(astNeuron.getName() +
                                  ": Equations or shapes could not be solved. The model remains unchanged.",
                                  Reporter.Level.ERROR);
          return astNeuron;
        }

        switch (solverOutput.solver) {
          case "exact":
            reporter.reportProgress("Equations are solved exactly.");
            workingVersion = exactSolutionTransformer.addExactSolution(workingVersion, solverOutput);
            break;

          case "numeric":
            reporter.reportProgress("Shapes will be solved with GLS.");
            workingVersion =  shapesToOdesTransformer.transformShapesToOdeForm(astNeuron, solverOutput);
            break;

          case "delta":
            return deltaSolutionTransformer.addExactSolution(solverOutput, astNeuron);

          default:
            reporter.reportProgress(astNeuron.getName() +
                                    ": Equations or shapes could not be solved. The model remains unchanged.");
            return workingVersion;
        }
      }
      else if (workingVersion.findEquationsBlock().get().getShapes().size() > 0 &&
               !odeShapeExists(workingVersion.findEquationsBlock().get().getShapes())) {
        reporter.reportProgress("Shapes will be solved with GLS.");
        final SolverOutput solverOutput = evaluator.solveShapes(deepCopy.findEquationsBlock().get().getShapes(), outputBase);
        workingVersion =  shapesToOdesTransformer.transformShapesToOdeForm(astNeuron, solverOutput);

      }
      else {
        applyIncomingSpikes(workingVersion);
      }

    }

    return workingVersion;
  }

  private boolean odeShapeExists(final List<ASTShape> shapes) {
    return shapes.stream().anyMatch(shape -> shape.getLhs().getDifferentialOrder().size() > 0);
  }

}
