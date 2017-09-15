/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTEquationsBlock;
import org.nest.nestml._ast.ASTNeuron;

import java.util.List;
import java.util.Map;

import static com.google.common.base.Preconditions.checkArgument;
import static java.util.stream.Collectors.toList;

/**
 * Takes SymPy result with the implicit form of ODEs (e.g replace shapes through a series of ODES) and replaces
 * the shapes through
 *
 * @author plotnikov
 */
class ShapesToOdesTransformer {

  ASTNeuron transformShapesToOdeForm(final ASTNeuron astNeuron, final SolverOutput solverOutput) {
    checkArgument(astNeuron.findEquationsBlock().isPresent());

    ASTNeuron workingVersion = TransformerBase.addVariablesToState(astNeuron, solverOutput.shape_state_variables);
    workingVersion = TransformerBase.addVariablesToInternals(workingVersion, solverOutput.initial_values);
    workingVersion = TransformerBase.removeShapes(workingVersion);
    TransformerBase.addShapeVariableUpdatesWithIncomingSpikes(
        solverOutput,
        workingVersion,
        TransformerBase.variableNameExtracter,
        TransformerBase.shapeNameExtracter);

    addStateShapeEquationsToEquationsBlock(solverOutput.shape_state_odes, workingVersion.findEquationsBlock().get());

    return workingVersion;
  }

  private void addStateShapeEquationsToEquationsBlock(
      final List<Map.Entry<String, String>> equationsFile,
      final ASTEquationsBlock astOdeDeclaration) {
    final List<ASTEquation> equations = equationsFile.stream()
        .map(ode -> ode.getKey() + "' = " + ode.getValue())
        .map(AstCreator::createEquation)
        .collect(toList());
    astOdeDeclaration.getEquations().addAll(equations);
  }

}
