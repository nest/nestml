/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.*;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;

/**
 * Takes SymPy result and the source AST. Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  private final SymPyOutput2NESTMLConverter converter2NESTML = new SymPyOutput2NESTMLConverter();

  public ASTNeuron addExactSolution(
      final ASTNeuron astNeuron,
      final Path pathToP00File,
      final Path PSCInitialValueFile,
      final Path stateStateVariablesFile,
      final Path stateVectorFile,
      final Path updateStepFile) {
    ASTNeuron workingVersion = addP30(astNeuron, pathToP00File);
    workingVersion = addPSCInitialValueAndHToInternalBlock(workingVersion, PSCInitialValueFile);
    workingVersion = addStateVariablesAndUpdateStatements(
        workingVersion,
        PSCInitialValueFile,
        stateStateVariablesFile,
        stateVectorFile);
    workingVersion = replaceODEPropagationStep(workingVersion, updateStepFile);

    return workingVersion;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addP30(
      final ASTNeuron astNeuron,
      final Path pathToP00File) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAliases(pathToP00File).get(0);

    astNeuron.getBody().addToInternalBlock(p00Declaration);
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addPSCInitialValueAndHToInternalBlock(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile) {
    final List<ASTAliasDecl> pscInitialValues = converter2NESTML.convertToAliases(pathPSCInitialValueFile);
    for (final ASTAliasDecl astAliasDecl:pscInitialValues) {
      final List<ASTVariable> variables = ASTNodes.getAll(astAliasDecl.getDeclaration(), ASTVariable.class);
      checkState(astNeuron.enclosingScopeIsPresent());
      // TODO can I do it better?
      final Scope scope = ((ScopeSpanningSymbol)astNeuron.getSymbol().get()).getSpannedScope(); // valid, after the symboltable is created

      Optional<VariableSymbol> vectorizedVariable = variables.stream()
          .map(astVariable -> (VariableSymbol) scope.resolve(astVariable.toString(), VariableSymbol.KIND).get())
          .filter(variableSymbol -> variableSymbol.getArraySizeParameter().isPresent())
          .findAny();
      if (vectorizedVariable.isPresent()) {
        // the existence of the array parameter is ensured by the query
        astAliasDecl.getDeclaration().setSizeParameter(vectorizedVariable.get().getArraySizeParameter().get());
      }

    }

    pscInitialValues.stream().forEach(initialValue -> astNeuron.getBody().addToInternalBlock(initialValue));
    astNeuron.getBody().addToInternalBlock(converter2NESTML.convertStringToAlias("h ms = resolution()"));

    return astNeuron;
  }

  ASTNeuron addStateVariablesAndUpdateStatements(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile,
      final Path stateVariablesFile,
      final Path stateUpdatesFile) {
    try {
      checkState(astNeuron.getBody().getEquations().isPresent(),  "The model has no ODES.");
      final ASTBody body = astNeuron.getBody();

      addStateVariables(stateVariablesFile, body);
      addStateUpdates(stateUpdatesFile, body);
      addPSCInitialValuesUpdates(pathPSCInitialValueFile, body);

      return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot solveODE stateVector output from the SymPy solver", e);
    }
  }

  private void addStateVariables(final Path stateVariablesFile, final ASTBody astBody) throws IOException {
    final List<String> stateVariableDeclarations = Files.lines(stateVariablesFile)
        .map(stateVariable -> stateVariable + " real")
        .collect(toList());

    stateVariableDeclarations.stream()
        .map(converter2NESTML::convertStringToAlias)
        .forEach(astBody::addToStateBlock);
  }

  private void addStateUpdates(final Path stateUpdatesFile, final ASTBody body) throws IOException {
    final List<String> stateUpdates = Files
        .lines(stateUpdatesFile)
        .collect(toList());


    final List<ASTAssignment> stateAssignments = stateUpdates
        .stream()
        .map(converter2NESTML::convertStringToAssignment)
        .collect(toList());

    final List<ASTDeclaration> tmpStateDeclarations = stateAssignments
        .stream()
        .map(assignment -> assignment.getVariableName() + " real = " + assignment.getVariableName())
        .map(converter2NESTML::convertStringToDeclaration)
        .collect(toList());

    final List<ASTAssignment> backAssignments = stateAssignments
        .stream()
        .map(assignment -> assignment.getVariableName().toString()) // get variable names as strings
        .map(stateVariable -> stateVariable.substring(0, stateVariable.indexOf("_tmp")) + " = " + stateVariable)
        .map(converter2NESTML::convertStringToAssignment)
        .collect(toList());

    tmpStateDeclarations.forEach(tmpDeclaration -> addDeclarationToDynamics(body, tmpDeclaration));
    stateAssignments.forEach(varAssignment -> addAssignmentToDynamics(body, varAssignment));
    backAssignments.forEach(varAssignment -> addAssignmentToDynamics(body, varAssignment));
  }

  private void addDeclarationToDynamics(
      final ASTBody astBodyDecorator,
      final ASTDeclaration astDeclaration) {
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    final ASTSimple_Stmt astSimpleStmt = SPLNodeFactory.createASTSimple_Stmt();
    final List<ASTSmall_Stmt> astSmallStmts = Lists.newArrayList();
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();

    astStmt.setSimple_Stmt(astSimpleStmt);
    astSmallStmts.add(astSmall_stmt);
    astSimpleStmt.setSmall_Stmts(astSmallStmts);

    astSmall_stmt.setDeclaration(astDeclaration);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }


  private void addPSCInitialValuesUpdates(final Path pathPSCInitialValueFile, final ASTBody body) {
    final List<ASTFunctionCall> i_sumCalls = ASTNodes.getAll(body.getEquations().get(), ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM))
        .collect(toList());

    final List<ASTAliasDecl> pscInitialValues = converter2NESTML.convertToAliases(pathPSCInitialValueFile);
    for (final ASTAliasDecl pscInitialValue:pscInitialValues) {
      final String pscInitialValueAsString = pscInitialValue.getDeclaration().getVars().get(0);
      final String variableName = pscInitialValueAsString.substring(0, pscInitialValueAsString.indexOf("PSCInitialValue"));
      final String shapeName = variableName.substring(variableName.indexOf("_") + 1, variableName.length());
      for (ASTFunctionCall i_sum_call:i_sumCalls) {
        final String shapeNameInCall = ASTNodes.toString(i_sum_call.getArgs().get(0));
        if (shapeNameInCall.equals(shapeName)) {
          final String bufferName = ASTNodes.toString(i_sum_call.getArgs().get(1));
          final ASTAssignment pscUpdateStep = converter2NESTML
              .convertStringToAssignment(variableName + " += " +  pscInitialValueAsString + " * "+ bufferName + ".getSum(t)");
          addAssignmentToDynamics(body, pscUpdateStep);
        }

      }

    }
  }

  private void addAssignmentToDynamics(
      final ASTBody astBodyDecorator,
      final ASTAssignment yVarAssignment) {
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    final ASTSimple_Stmt astSimpleStmt = SPLNodeFactory.createASTSimple_Stmt();
    final List<ASTSmall_Stmt> astSmallStmts = Lists.newArrayList();
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();

    astStmt.setSimple_Stmt(astSimpleStmt);
    astSmallStmts.add(astSmall_stmt);
    astSimpleStmt.setSmall_Stmts(astSmallStmts);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(yVarAssignment);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }

  ASTNeuron replaceODEPropagationStep(final ASTNeuron astNeuron, final Path updateStepFile) {

    final ASTBody astBodyDecorator = astNeuron.getBody();
    final IntegrateFunctionCollector odeCollector = new IntegrateFunctionCollector();

    try {
      final List<ASTSmall_Stmt> propogatorSteps = Files.lines(updateStepFile)
          .map(converter2NESTML::convertStringToAssignment)
          .map(this::convertToSmallStatement)
          .collect(toList());
      odeCollector.startVisitor(astBodyDecorator.getDynamics().get(0));

      if (odeCollector.getFoundOde().isPresent()) {
        final Optional<ASTNode> smallStatement = ASTNodes.getParent(odeCollector.getFoundOde().get(), astNeuron);
        checkState(smallStatement.isPresent());
        checkState(smallStatement.get() instanceof ASTSmall_Stmt);
        final ASTSmall_Stmt integrateCall = (ASTSmall_Stmt) smallStatement.get();

        final Optional<ASTNode> simpleStatement = ASTNodes.getParent(smallStatement.get(), astNeuron);
        checkState(simpleStatement.isPresent());
        checkState(simpleStatement.get() instanceof ASTSimple_Stmt);
        final ASTSimple_Stmt astSimpleStatement = (ASTSimple_Stmt) simpleStatement.get();
        int integrateFunction = astSimpleStatement.getSmall_Stmts().indexOf(integrateCall);
        astSimpleStatement.getSmall_Stmts().remove(integrateCall);
        astSimpleStatement.getSmall_Stmts().addAll(integrateFunction, propogatorSteps);

        return astNeuron;
      } else {
        Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
        return astNeuron;
      }
    } catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  private ASTSmall_Stmt convertToSmallStatement(final ASTAssignment astAssignment) {
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();
    astSmall_stmt.setAssignment(astAssignment);
    return astSmall_stmt;
  }

  private class IntegrateFunctionCollector implements NESTMLInheritanceVisitor {
    // Initialized by null and set to the actual value
    private ASTFunctionCall foundOde = null;

    void startVisitor(ASTNESTMLNode node) {
      node.accept(this);
    }

    @Override
    public void visit(final ASTFunctionCall astFunctionCall) {
      // TODO actually works only for the first ode
      if (astFunctionCall.getCalleeName().equals("integrate")) {
        foundOde = astFunctionCall;
      }
    }

    Optional<ASTFunctionCall> getFoundOde() {
      return Optional.ofNullable(foundOde);
    }

  }

}
