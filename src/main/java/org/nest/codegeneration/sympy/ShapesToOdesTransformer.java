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
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;

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

  ASTNeuron transformShapesToOdeForm(final SolverOutput solverOutput, final ASTNeuron astNeuron) {
    checkArgument(astNeuron.getBody().getODEBlock().isPresent());

    ASTNeuron workingVersion = addVariablesToState(astNeuron, solverOutput.shape_state_variables);
    workingVersion = addVariablesToInternals(workingVersion, solverOutput.initial_values);
    workingVersion = replaceShapesThroughVariables(workingVersion);
    addUpdatesWithPSCInitialValue(
        solverOutput,
        workingVersion.getBody(),
        variableNameExtracter,
        shapeNameExtracter);

    addShapeEquationsToEquationsBlock(solverOutput.shape_state_odes, workingVersion.getBody().getODEBlock().get());

    System.out.println("!!!!!!!!!!!!!Start DEBUG!!!!!!!!!!!!!!!!!");
    System.out.println(NESTMLPrettyPrinter.Builder.build().print(workingVersion));
    System.out.println("!!!!!!!!!!!!!End DEBUG!!!!!!!!!!!!!!!!!");
    return workingVersion;
  }

  private void addShapeEquationsToEquationsBlock(
      final List<Map.Entry<String, String>> equationsFile,
      final ASTOdeDeclaration astOdeDeclaration) {
    final List<ASTEquation> equations = equationsFile.stream()
        .map(ode -> ode.getKey() + " = " + ode.getValue())
        .map(AstCreator::createEquation)
        .collect(toList());
    astOdeDeclaration.getODEs().addAll(equations);
  }

  private ASTNeuron replaceShapesThroughVariables(ASTNeuron astNeuron) {
    final List<ASTDeclaration> stateVariablesDeclarations = shapesToStateVariables(
        astNeuron.getBody().getODEBlock().get());
    stateVariablesDeclarations.forEach(stateVariable -> astNeuron.getBody().addToStateBlock(stateVariable));
    astNeuron.getBody().getODEBlock().get().getShapes().clear();
    return astNeuron;
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
