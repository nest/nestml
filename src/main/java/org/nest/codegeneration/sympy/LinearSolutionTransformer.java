/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.*;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.reporting.Reporter;

import java.util.List;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static com.google.common.collect.Lists.newArrayList;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.AstCreator.createDeclaration;
import static org.nest.nestml._symboltable.symbols.VariableSymbol.resolve;

/**
 * Takes SymPy result with the linear solution of the ODE and the source AST.
 * Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class LinearSolutionTransformer extends TransformerBase {
  // example initial value av__I_shape_in__1
  // the shape state variable is `I_shape_in__1`
  // the shape name is `I_shape_in`
  private final Function<String, String> variableNameExtracter
      = initialValue -> initialValue.substring("av__".length());

  private final Function<String, String> shapeNameExtracter = initialValue -> {
    return initialValue.substring("av__".length(), initialValue.lastIndexOf("__"));
  };


  public ASTNeuron addExactSolution(
      final ASTNeuron astNeuron,
      final SolverOutput solverOutput) {
    ASTNeuron workingVersion = astNeuron;
    workingVersion.getBody().addToInternalBlock(createDeclaration("__h ms = resolution()"));

    workingVersion = addVariableToInternals(astNeuron, solverOutput.ode_var_factor);
    workingVersion = addVariableToInternals(astNeuron, solverOutput.const_input);
    workingVersion = addVariablesToInternals(workingVersion, solverOutput.initial_values);
    workingVersion = addVariablesToInternals(workingVersion, solverOutput.propagator_elements);
    workingVersion = addVariablesToState(workingVersion, solverOutput.shape_state_variables);
    workingVersion = addShapeStateUpdatesToUpdateBlock(workingVersion, solverOutput);

    // oder is important, otherwise addShapeStateUpdatesToUpdateBlock will try to resolve state variables,
    // for which nor symbol are added. TODO filter them
    workingVersion = replaceIntegrateCallThroughPropagation(workingVersion, solverOutput.ode_var_update_instructions);
    System.out.println("!!!!!!!!!!!!!Start DEBUG!!!!!!!!!!!!!!!!!");
    System.out.println(NESTMLPrettyPrinter.Builder.build().print(workingVersion));
    System.out.println("!!!!!!!!!!!!!End DEBUG!!!!!!!!!!!!!!!!!");
    return workingVersion;
  }

  private ASTNeuron addShapeStateUpdatesToUpdateBlock(final ASTNeuron astNeuron, final SolverOutput solverOutput) {
    final ASTBody body = astNeuron.getBody();

    addStateUpdates(solverOutput, body);
    addUpdatesWithPSCInitialValue(solverOutput, body, variableNameExtracter, shapeNameExtracter);

    return astNeuron;
  }

  ASTNeuron addVariablesToState(final ASTNeuron astNeuron, final List<String> shapeStateVariables) {
    checkState(astNeuron.getBody().getEnclosingScope().isPresent());
    final Scope scope = astNeuron.getBody().getEnclosingScope().get();

    final List<VariableSymbol> correspondingShapeSymbols = shapeStateVariables
        .stream()
        .map(this::getShapeNameFromStateVariable)
        .map(shapeName -> resolve(shapeName, scope))
        .collect(Collectors.toList());

    for (int i = 0; i < shapeStateVariables.size(); ++i) {
      final String vectorDatatype = correspondingShapeSymbols.get(i).isVector()?"[" + correspondingShapeSymbols.get(i).getVectorParameter().get() + "]":"";
      final String stateVarDeclaration = shapeStateVariables.get(i) + " real " + vectorDatatype;

      astNeuron.getBody().addToStateBlock(createDeclaration(stateVarDeclaration));
    }

    return astNeuron;
  }

  private void addStateUpdates(final SolverOutput solverOutput, final ASTBody astBody)  {

    solverOutput.updates_to_shape_state_variables
        .stream()
        .map(update -> update.getKey() + " = " + update.getValue())
        .map(AstCreator::createAssignment)
        .forEach(astAssignment -> addAssignmentToDynamics(astAssignment, astBody));
  }

  // TODO: enable the optimization
  private List<ASTAssignment> computeShapeUpdates(final SolverOutput solverOutput, final ASTBody astBody) {

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
    stateVariableNames.addAll(astBody.getStateSymbols()
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
        astBody.addToInternalBlock(aliasAst);
      }

    }*/
    return stateUpdatesASTs;
  }

  private String printVectorParameter(Optional<VariableSymbol> vectorizedVariable) {
    return vectorizedVariable.map(variableSymbol -> "[" + variableSymbol.getVectorParameter().get() + "]").orElse("");
  }


  /**
   * For every oder of the shape a variable of the typ shape_name__order is created. This function extracts the shape
   * name.
   * @param shapeStateVariable Statevariable name generated by the solver script
   * @return Shapename as a string
   */
  private String getShapeNameFromStateVariable(final String shapeStateVariable) {
    return shapeStateVariable.substring(0, shapeStateVariable.lastIndexOf("__"));
  }

  private void addDeclarationToDynamics(
      final ASTBody astBodyDecorator,
      final ASTDeclaration astDeclaration) {
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();
    astStmt.setSmall_Stmt(astSmall_stmt);

    astSmall_stmt.setDeclaration(astDeclaration);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }



}
