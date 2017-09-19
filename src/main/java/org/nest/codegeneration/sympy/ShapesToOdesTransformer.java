/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTEquationsBlock;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTShape;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.google.common.base.Preconditions.checkArgument;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.TransformerBase.computeShapeStateVariablesWithInitialValues;

/**
 * Takes SymPy result with the implicit form of ODEs (e.g replace shapes through a series of ODES) and replaces
 * the shapes through
 *
 * @author plotnikov
 */
class ShapesToOdesTransformer {

  ASTNeuron transformShapesToOdeForm(final ASTNeuron astNeuron, final SolverOutput solverOutput) {
    checkArgument(astNeuron.findEquationsBlock().isPresent());

    List<Map.Entry<String, String>> stateShapeVariablesWithInitialValues = computeShapeStateVariablesWithInitialValues(solverOutput);
    ASTNeuron workingVersion = TransformerBase.addVariablesToInitialValues(astNeuron, stateShapeVariablesWithInitialValues);

    // TODO actually, only shapes that are solved must be reseted
    astNeuron.removeShapes();
    addStateShapeEquationsToEquationsBlock(solverOutput.shape_state_odes, workingVersion.findEquationsBlock().get());
    return workingVersion;
  }

  private void addStateShapeEquationsToEquationsBlock(
      final List<Map.Entry<String, String>> equationsFile,
      final ASTEquationsBlock astOdeDeclaration) {
    final List<ASTShape> astShapes = equationsFile.stream()
        .map(ode -> "shape " + ode.getKey() + "' = " + ode.getValue())
        .map(AstCreator::createShape)
        .collect(toList());
    astOdeDeclaration.getShapes().addAll(astShapes);
  }

}
