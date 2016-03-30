/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.se_rwth.commons.logging.Log;
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
import java.util.Collections;
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
      final Path stateVectorFile,
      final Path updateStepFile) {
    ASTNeuron workingVersion = addP30(astNeuron, pathToP00File);
    workingVersion = addPSCInitialValue(workingVersion, PSCInitialValueFile);
    workingVersion = addStateVariablesAndUpdateStatements(workingVersion, stateVectorFile);
    workingVersion = replaceODE(workingVersion, updateStepFile);

    return workingVersion;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addP30(
      final ASTNeuron astNeuron,
      final Path pathToP00File) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAlias(pathToP00File);

    astNeuron.getBody().addToInternalBlock(p00Declaration);
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addPSCInitialValue(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile) {

    final ASTAliasDecl pscInitialValue = converter2NESTML.convertToAlias(pathPSCInitialValueFile);

    astNeuron.getBody().addToInternalBlock(pscInitialValue);
    return astNeuron;
  }

  ASTNeuron addStateVariablesAndUpdateStatements(
      final ASTNeuron astNeuron,
      final Path stateVectorFile) {
    try {
      final List<String> stateVectorLines = Files
          .lines(stateVectorFile)
          .collect(Collectors.toList());

      Collections.reverse(stateVectorLines);

      checkState(stateVectorLines.size() > 0, "False stateVector.mat format. Check SymPy solver.");
      checkState(astNeuron.getBody().getEquations().isPresent(),  "The model has no ODES.");

      // First entry is the number of variables
      final Integer stateVariablesNumber = stateVectorLines.size();

      final List<String> stateVariableDeclarations = Lists.newArrayList();
      for (int i = 1; i <= stateVariablesNumber; ++i) {
        stateVariableDeclarations.add("y"+ i + " real");
      }

      stateVariableDeclarations.stream()
          .map(converter2NESTML::convertStringToAlias)
          .forEach(astAliasDecl -> astNeuron.getBody().addToStateBlock(astAliasDecl));

      // remaining entries are y_index update entries
      // these statements must be printed at the end of the dynamics function
      ASTBody body = astNeuron.getBody();
      stateVectorLines
          .stream()
          .map(converter2NESTML::convertStringToAssignment)
          .forEach(varAssignment -> addAssignmentToDynamics(body, varAssignment));

      final List<ASTFunctionCall> functions = ASTNodes.getAll(astNeuron.getBody().getEquations().get(), ASTFunctionCall.class)
          .stream()
          .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM))
          .collect(toList());

      for (ASTFunctionCall i_sum_call:functions) {
        final String bufferName = ASTNodes.toString(i_sum_call.getArgList().getArgs().get(1));
        final ASTAssignment pscUpdateStep = converter2NESTML
            .convertStringToAssignment("y1 += PSCInitialValue * " + bufferName + ".getSum(t)");
        addAssignmentToDynamics(body, pscUpdateStep);
      }

      return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot solveODE stateVector output from the SymPy solver", e);
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

  private void addAssignmentToDynamics(ASTBody astBodyDecorator,
      ASTAssignment yVarAssignment) {
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


}
