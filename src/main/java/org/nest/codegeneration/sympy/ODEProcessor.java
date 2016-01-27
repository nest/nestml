/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.SolverType;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTOdeDeclaration;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static de.se_rwth.commons.logging.Log.warn;

/**
 * Analyzes a neuron for defined ODE. If an ode is defined, it produces a temporary NESTML model
 * with the exact solution if possible or creates an explicit form of the ODEs.
 *
 * @author plotnikov
 */
public class ODEProcessor {
  private final String LOG_NAME = ODEProcessor.class.getName();

  private final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();

  public ASTNESTMLCompilationUnit process(
      final ASTNESTMLCompilationUnit root,
      final Path outputBase) {
    checkState(root.getNeurons().size() > 0);
    final ASTNeuron neuron = root.getNeurons().get(0);
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(neuron.getBody());
    if (astBodyDecorator.getEquations().isPresent()) {
      return handleNeuronWithODE(root, outputBase);
    }
    else {
      final String msg = "The neuron: " + neuron.getName() +
          " doesn't contain ODE. The analysis is skipped.";
      Log.warn(msg);
      return root;
    }

  }

  protected ASTNESTMLCompilationUnit handleNeuronWithODE(
      final ASTNESTMLCompilationUnit root,
      final Path outputBase) {
    final Optional<Path> generatedScript = SymPyScriptGenerator.generateSympyODEAnalyzer(
        root.getNeurons().get(0),
        outputBase);

    checkState(generatedScript.isPresent());

    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
    boolean successfulExecution = evaluator.execute(generatedScript.get());
    checkState(successfulExecution, "Error during solver script evaluation.");
    final Path odeTypePath = Paths.get(outputBase.toString(), SymPyScriptEvaluator.ODE_TYPE);
    final SolverType solutionType = SolverType.fromFile(odeTypePath);

    if (solutionType.equals(SolverType.EXACT)) {
      info("ODE is solved exactly.", LOG_NAME);
      final ASTNESTMLCompilationUnit transformedModel = exactSolutionTransformer
          .replaceODEWithSymPySolution(
              root,
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.P30_FILE),
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE),
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.STATE_VECTOR_FILE),
              Paths.get(outputBase.toString(), SymPyScriptEvaluator.UPDATE_STEP_FILE));

      return transformedModel;
    }
    else if (solutionType.equals(SolverType.NUMERIC)) {
      info("ODE is solved numerically.", LOG_NAME);
      return root;
    }
    else {
      warn("ODEs could not be solved. The model remains unchanged.");
      return root;
    }

  }

  public ExactSolutionTransformer getExactSolutionTransformer() {
    return exactSolutionTransformer;
  }
}
