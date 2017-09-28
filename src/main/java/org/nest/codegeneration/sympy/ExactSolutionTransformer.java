/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.reporting.Reporter;

import java.util.List;
import java.util.Map;
import java.util.Set;

import static com.google.common.collect.Lists.newArrayList;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;
import static org.nest.codegeneration.sympy.AstCreator.createDeclaration;
import static org.nest.codegeneration.sympy.TransformerBase.*;

/**
 * Takes SymPy result with the linear solution of the ODE and the source AST.
 * Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
class ExactSolutionTransformer {

  ASTNeuron addExactSolution(
      final ASTNeuron astNeuron,
      final SolverOutput solverOutput) {
    ASTNeuron workingVersion = astNeuron;
    workingVersion.addToInternalBlock(createDeclaration("__h ms = resolution()"));

    workingVersion = addVariableToInternals(workingVersion, solverOutput.ode_var_factor);
    workingVersion = addVariableToInternals(workingVersion, solverOutput.const_input);
    workingVersion = addVariablesToInternals(workingVersion, solverOutput.propagator_elements);

    final List<Map.Entry<String, String>> stateShapeVariablesWithInitialValues =
        computeShapeStateVariablesWithInitialValues(solverOutput);

    // copy initial block variables to the state block, since they are not backed through an ODE.
    astNeuron.getInitialValuesDeclarations().forEach(astNeuron::addToStateBlock);

    workingVersion = addVariablesToInitialValues(workingVersion, stateShapeVariablesWithInitialValues);
    addStateUpdates(solverOutput, workingVersion);

    workingVersion = TransformerBase.replaceIntegrateCallThroughPropagation(
        workingVersion,
        solverOutput.ode_var_update_instructions);

    applyIncomingSpikes(workingVersion);

    // get rid of the ODE stuff since the model is solved exactly and all ODEs are removed.
    workingVersion.removeEquationsBlock();

    stateShapeVariablesWithInitialValues
        .stream()
        .map(Map.Entry::getKey)
        .map(shapeStateVariable -> createDeclaration(shapeStateVariable + " real"))
        .forEach(astNeuron::addToStateBlock);

    workingVersion.getInitialValuesBlock().ifPresent(block -> block.getDeclarations().clear());

    // since there is no
    return workingVersion;
  }

  private void addStateUpdates(final SolverOutput solverOutput, final ASTNeuron astNeuron)  {
    final Set<String> tempVariables = solverOutput.updates_to_shape_state_variables
        .stream()
        .map(Map.Entry::getKey)
        .filter(update -> update.startsWith("__tmp"))
        .collect(toSet());

    tempVariables
        .stream()
        .map(update -> update + " real")
        .map(AstCreator::createDeclaration)
        .forEach(astAssignment -> TransformerBase.addDeclarationToUpdateBlock(astAssignment, astNeuron));

    solverOutput.updates_to_shape_state_variables
        .stream()
        .map(update -> update.getKey() + " = " + update.getValue())
        .map(AstCreator::createAssignment)
        .forEach(astAssignment -> TransformerBase.addAssignmentToUpdateBlock(astAssignment, astNeuron));
  }

  // TODO: enable the optimization
  private List<ASTAssignment> computeShapeUpdates(final SolverOutput solverOutput, final ASTNeuron astNeuron) {

    final List<ASTAssignment> stateUpdatesASTs = solverOutput.updates_to_shape_state_variables
        .stream()
        .map(shapeStateUpdate -> shapeStateUpdate.getKey() + " = " + shapeStateUpdate.getValue())
        .map(AstCreator::createAssignment)
        .collect(toList());

    final List<ASTExpr> rhsExpressions = stateUpdatesASTs
        .stream()
        .map(ASTAssignment::getExpr)
        .collect(toList());

    final List<String> stateVariableNames = newArrayList();
    stateVariableNames.addAll(astNeuron.getStateSymbols()
        .stream()
        .map(VariableSymbol::getName)
        .collect(toList()));

    Reporter.get().reportProgress("TODO: activate the folder optimization");
    /*
    stateVariableNames.addAll(solverOutput.shape_state_variables);

    for (int i = 0; i < rhsExpressions.size(); ++i) {
      final ASTExpr expr = rhsExpressions.get(i);
      final ExpressionFolder expressionFolder = new ExpressionFolder();
      // now, variables in the expression are replaced, but they would be undefined in the model
      // and they are changed in the expressions stored in stateUpdatesASTs
      expressionFolder.fold(expr, stateVariableNames, "__P" + i);
      // add these additional variables to the internal block
      final List<ASTExpr> nodesToReplace = expressionFolder.getNodesToReplace();
      final List<String> tmpInternalVariables = expressionFolder.getInternalVariables();
      for (int j = 0; j < nodesToReplace.size(); ++j) {
        final Optional<VariableSymbol> vectorizedVariable = getVectorizedVariable(nodesToReplace.get(j), scope);
        final ASTDeclaration aliasAst = createDeclaration(tmpInternalVariables.get(j) + " real " + printVectorParameter(vectorizedVariable) + " = " + printer.print(nodesToReplace.get(j)));
        astNeuron.addToInternalBlock(aliasAst);
      }

    }*/
    return stateUpdatesASTs;
  }

  /*
  private String printVectorParameter(Optional<VariableSymbol> vectorizedVariable) {
    return vectorizedVariable.map(variableSymbol -> "[" + variableSymbol.getVectorParameter().get() + "]").orElse("");
  }
  */

}
