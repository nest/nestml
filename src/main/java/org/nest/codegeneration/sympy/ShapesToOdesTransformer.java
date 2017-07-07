/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOdeDeclaration;

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
class ShapesToOdesTransformer extends TransformerBase {

  ASTNeuron transformShapesToOdeForm(final ASTNeuron astNeuron, final SolverOutput solverOutput) {
    checkArgument(astNeuron.getBody().getOdeBlock().isPresent());

    ASTNeuron workingVersion = addVariablesToState(astNeuron, solverOutput.shape_state_variables);
    workingVersion = addVariablesToInternals(workingVersion, solverOutput.initial_values);
    workingVersion = removeShapes(workingVersion);
    addUpdatesWithPSCInitialValues(
        solverOutput,
        workingVersion.getBody(),
        variableNameExtracter,
        shapeNameExtracter);

    addStateShapeEquationsToEquationsBlock(solverOutput.shape_state_odes, workingVersion.getBody().getOdeBlock().get());
    return workingVersion;
  }

  private void addStateShapeEquationsToEquationsBlock(
      final List<Map.Entry<String, String>> equationsFile,
      final ASTOdeDeclaration astOdeDeclaration) {
    final List<ASTEquation> equations = equationsFile.stream()
        .map(ode -> ode.getKey() + "' = " + ode.getValue())
        .map(AstCreator::createEquation)
        .collect(toList());
    astOdeDeclaration.getODEs().addAll(equations);
  }

  private List<ASTDeclaration> shapesToStateVariables(final ASTOdeDeclaration astOdeDeclaration) {
    final List<String> stateVariables = astOdeDeclaration.getShapes()
        .stream()
        .map(shape -> shape.getLhs().toString())
        .collect(toList());

    return stateVariables
        .stream()
        .map(variable -> variable + " real")
        .map(AstCreator::createDeclaration)
        .collect(toList());
  }

}
