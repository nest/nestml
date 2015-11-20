/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Analyzes a neuron for defined ODE. If an ode is defined, it produces a temporary NESTML model
 * with the exact solution if possible.
 *
 * @author plotnikov
 */
public class ODEProcessor {

  private final SymPySolutionTransformer symPySolutionTransformer = new SymPySolutionTransformer();

  public ASTNESTMLCompilationUnit process(
      final ASTNESTMLCompilationUnit root,
      final File outputBase) {
    checkState(root.getNeurons().size() > 0);
    final ASTNeuron neuron = root.getNeurons().get(0);
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(neuron.getBody());
    if (astBodyDecorator.getOdeDefinition().isPresent()) {
      return handleNeuronWithODE(root, outputBase);
    }
    else {
      return root;
    }

  }

  private ASTNESTMLCompilationUnit handleNeuronWithODE(
      final ASTNESTMLCompilationUnit root,
      final File outputBase) {

    final File outputFolder = new File(Paths.get(outputBase.getPath(), root.getNeurons().get(0).getName()).toString());
    final Optional<Path> generatedScript = SymPyScriptGenerator.generateSympyODEAnalyzer(
        root.getNeurons().get(0),
        outputFolder);

    checkState(generatedScript.isPresent());

    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();
    checkState(evaluator.execute(generatedScript.get()));


    final ASTNESTMLCompilationUnit transformedModel = symPySolutionTransformer
        .replaceODEWithSymPySolution(
            root,
            Paths.get(outputFolder.getPath(), SymPyScriptEvaluator.P30_FILE).toString(),
            Paths.get(outputFolder.getPath(), SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE).toString(),
            Paths.get(outputFolder.getPath(), SymPyScriptEvaluator.STATE_VECTOR_FILE).toString(),
            Paths.get(outputFolder.getPath(), SymPyScriptEvaluator.UPDATE_STEP_FILE).toString());

    return transformedModel;
  }

}
