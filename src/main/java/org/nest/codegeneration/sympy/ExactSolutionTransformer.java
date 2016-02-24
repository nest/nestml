/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.spl._ast.*;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;

/**
 * Takes SymPy result and the source AST. Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  final SymPyOutput2NESTMLConverter converter2NESTML = new SymPyOutput2NESTMLConverter();

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
  public ASTNeuron addP30(
      final ASTNeuron root,
      final Path pathToP00File) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAlias(pathToP00File);

    addToInternalBlock(root, p00Declaration);
    return root;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  public ASTNeuron addPSCInitialValue(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile) {

    final ASTAliasDecl pscInitialValue = converter2NESTML.convertToAlias(pathPSCInitialValueFile);

    return addToInternalBlock(astNeuron, pscInitialValue);
  }

  public ASTNeuron addStateVariablesAndUpdateStatements(
      final ASTNeuron astNeuron,
      final Path stateVectorFile) {
    try {
      final List<String> stateVectorLines = Files
          .lines(stateVectorFile)
          .collect(Collectors.toList());

      Collections.reverse(stateVectorLines);

      checkState(stateVectorLines.size() > 0, "False stateVector.mat format. Check SymPy solver.");

      // First entry is the number of variables
      final Integer stateVariablesNumber = stateVectorLines.size();

      final List<String> stateVariableDeclarations = Lists.newArrayList();
      for (int i = 1; i <= stateVariablesNumber; ++i) {
        stateVariableDeclarations.add("y"+ i + " real");
      }

      stateVariableDeclarations.stream()
          .map(converter2NESTML::convertStringToAlias)
          .forEach(astAliasDecl -> addToStateBlock(astNeuron, astAliasDecl));

      // remaining entries are y_index update entries
      // these statements must be printed at the end of the dynamics function
      ASTBody body = astNeuron.getBody();
      stateVectorLines
          .stream()
          .map(converter2NESTML::convertStringToAssignment)
          .forEach(varAssignment -> addAssignmentToDynamics(body, varAssignment));

      // add extra handling of the y0 variable
      final NeuronSymbol neuronSymbol = (NeuronSymbol) astNeuron.getSymbol().get();

      if (!neuronSymbol.getSpikeBuffers().isEmpty()) {
        final VariableSymbol spikeBuffer = neuronSymbol.getSpikeBuffers().get(0);
        final ASTAssignment pscUpdateStep = converter2NESTML
            .convertStringToAssignment("y1 += PSCInitialValue * " + spikeBuffer.getName() + ".getSum(t)");
        addAssignmentToDynamics(body, pscUpdateStep);
      }
      return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot solveODE stateVector output from the SymPy solver", e);
    }
  }

  public ASTNeuron replaceODE(final ASTNeuron astNeuron, final Path updateStepFile) {
    final ASTAssignment stateUpdate = converter2NESTML.convertToAssignment(updateStepFile);

    final ASTBody astBodyDecorator = astNeuron.getBody();

    final ODECollector odeCollector = new ODECollector();
    odeCollector.startVisitor(astBodyDecorator.getDynamics().get(0));
    if (!odeCollector.getFoundOde().isPresent()) {
      Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
      return astNeuron;
    }

    final Optional<ASTNode> parent = ASTNodes.getParent(odeCollector.getFoundOde().get(), astNeuron);
    checkState(parent.isPresent());
    checkState(parent.get() instanceof ASTSmall_Stmt);

    final ASTSmall_Stmt castedParent = (ASTSmall_Stmt) parent.get();
    castedParent.setAssignment(stateUpdate);

    return astNeuron;
  }

  private class ODECollector implements NESTMLVisitor {
    private Optional<ASTFunctionCall> foundOde = Optional.empty();

    public void startVisitor(ASTNESTMLNode node) {
      node.accept(this);
    }

    @Override
    public void visit(final ASTFunctionCall astFunctionCall) {
      // TODO also parameter should be checked
      // TODO actually works only for the first ode
      if (astFunctionCall.getCalleeName().equals("integrate")) {
        foundOde = Optional.of(astFunctionCall);
      }
    }

    public Optional<ASTFunctionCall> getFoundOde() {
      return foundOde;
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

  // TODO do I need functions? Try to express it as lambda
  private ASTNeuron addToInternalBlock(
      final ASTNeuron astNeuron,
      final ASTAliasDecl declaration) {
    final ASTBody astBody = astNeuron.getBody();
    astBody.addToInternalBlock(declaration);
    return astNeuron;
  }

  private void addToStateBlock(
      final ASTNeuron astNeuron,
      final ASTAliasDecl declaration) {
    final ASTBody astBodyDecorator = astNeuron.getBody();
    astBodyDecorator.addToStateBlock(declaration);
  }

}
