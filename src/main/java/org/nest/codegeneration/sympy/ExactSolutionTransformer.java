/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.*;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;

/**
 * Takes SymPy result and the source AST. Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  private final SymPyOutput2NESTMLConverter converter2NESTML = new SymPyOutput2NESTMLConverter();

  public ASTNeuron replaceODEWithSymPySolution(
      final ASTNeuron astNeuron,
      final Path pathToP00File,
      final Path PSCInitialValueFile,
      final Path stateStateVariablesFile,
      final Path stateVectorFile,
      final Path updateStepFile) {
    ASTNeuron workingVersion = addP30(astNeuron, pathToP00File);
    workingVersion = addPSCInitialValueToStateBlock(workingVersion, PSCInitialValueFile);
    workingVersion = addStateVariablesAndUpdateStatements(
        workingVersion,
        PSCInitialValueFile,
        stateStateVariablesFile,
        stateVectorFile);
    workingVersion = replaceODE(workingVersion, updateStepFile);

    return workingVersion;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addP30(
      final ASTNeuron astNeuron,
      final Path pathToP00File) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAlias(pathToP00File).get(0);

    astNeuron.getBody().addToInternalBlock(p00Declaration);
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addPSCInitialValueToStateBlock(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile) {
    final List<ASTAliasDecl> pscInitialValue = converter2NESTML.convertToAlias(pathPSCInitialValueFile);
    pscInitialValue.stream().forEach(initialValue -> astNeuron.getBody().addToInternalBlock(initialValue));
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
        .collect(Collectors.toList());

    stateVariableDeclarations.stream()
        .map(converter2NESTML::convertStringToAlias)
        .forEach(astBody::addToStateBlock);
  }

  private void addStateUpdates(final Path stateUpdatesFile, final ASTBody body) throws IOException {
    final List<String> stateUpdates = Files
        .lines(stateUpdatesFile)
        .collect(Collectors.toList());


    final List<ASTAssignment> stateAssignments = stateUpdates
        .stream()
        .map(converter2NESTML::convertStringToAssignment)
        .collect(Collectors.toList());

    final List<ASTDeclaration> tmpStateDeclarations = stateAssignments
        .stream()
        .map(assignment -> assignment.getVariableName() + " real = " + assignment.getVariableName())
        .map(converter2NESTML::convertStringToDeclaration)
        .collect(Collectors.toList());

    final List<ASTAssignment> backAssignments = stateAssignments
        .stream()
        .map(assignment -> assignment.getVariableName().toString()) // get variable names as strings
        .map(stateVariable -> stateVariable.substring(0, stateVariable.indexOf("_tmp")) + " = " + stateVariable)
        .map(converter2NESTML::convertStringToAssignment)
        .collect(Collectors.toList());

    tmpStateDeclarations.forEach(tmpDeclaration -> addDeclarationToDynamics(body, tmpDeclaration));
    stateAssignments.forEach(varAssignment -> addAssignmentToDynamics(body, varAssignment));
    backAssignments.forEach(varAssignment -> addAssignmentToDynamics(body, varAssignment));
  }

  private void addPSCInitialValuesUpdates(final Path pathPSCInitialValueFile, final ASTBody body) {
    final List<ASTFunctionCall> i_sumCalls = ASTNodes.getAll(body.getEquations().get(), ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM))
        .collect(toList());

    final List<ASTAliasDecl> pscInitialValues = converter2NESTML.convertToAlias(pathPSCInitialValueFile);
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

  ASTNeuron replaceODE(final ASTNeuron astNeuron, final Path updateStepFile) {
    final ASTAssignment stateUpdate = converter2NESTML.convertToAssignment(updateStepFile);

    final ASTBody astBodyDecorator = astNeuron.getBody();

    final IntegrateFunctionCollector odeCollector = new IntegrateFunctionCollector();
    odeCollector.startVisitor(astBodyDecorator.getDynamics().get(0));
    if (odeCollector.getFoundOde().isPresent()) {

      final Optional<ASTNode> parent = ASTNodes.getParent(odeCollector.getFoundOde().get(), astNeuron);
      checkState(parent.isPresent());
      checkState(parent.get() instanceof ASTSmall_Stmt);

      final ASTSmall_Stmt castedParent = (ASTSmall_Stmt) parent.get();
      castedParent.setAssignment(stateUpdate);
      return astNeuron;
    }
    else {
      Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
      return astNeuron;
    }

  }

  private class IntegrateFunctionCollector implements NESTMLInheritanceVisitor {
    // Initialized by null and set to the actual value
    private ASTFunctionCall foundOde = null;

    void startVisitor(ASTNESTMLNode node) {
      node.accept(this);
    }

    @Override
    public void visit(final ASTFunctionCall astFunctionCall) {
      // TODO also parameter should be checked
      // TODO actually works only for the first ode
      if (astFunctionCall.getCalleeName().equals("integrate")) {
        foundOde = astFunctionCall;
      }
    }

    Optional<ASTFunctionCall> getFoundOde() {
      return Optional.ofNullable(foundOde);
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


}
