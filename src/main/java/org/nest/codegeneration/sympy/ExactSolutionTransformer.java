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
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNESTMLNode;
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
import static de.se_rwth.commons.Names.getQualifiedName;

/**
 * Takes SymPy result and the source AST. Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  final SymPyOutput2NESTMLConverter converter2NESTML = new SymPyOutput2NESTMLConverter();

  public ASTNESTMLCompilationUnit replaceODEWithSymPySolution(
      ASTNESTMLCompilationUnit root,
      final Path pathToP00File,
      final Path PSCInitialValueFile,
      final Path stateVectorFile,
      final Path updateStepFile) {
    root = addP30(root, pathToP00File);
    root = addPSCInitialValue(root, PSCInitialValueFile);
    root = addStateVariablesAndUpdateStatements(root, stateVectorFile);
    root = replaceODE(root, updateStepFile);

    return root;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  public ASTNESTMLCompilationUnit addP30(
      final ASTNESTMLCompilationUnit root,
      final Path pathToP00File) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAlias(pathToP00File);

    addToInternalBlock(root, p00Declaration);
    return root;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  public ASTNESTMLCompilationUnit addPSCInitialValue(
      final ASTNESTMLCompilationUnit root,
      final Path pathPSCInitialValueFile) {

    final ASTAliasDecl pscInitialValue = converter2NESTML.convertToAlias(pathPSCInitialValueFile);

    addToInternalBlock(root, pscInitialValue);
    return root;
  }

  public ASTNESTMLCompilationUnit addStateVariablesAndUpdateStatements(
      final ASTNESTMLCompilationUnit root,
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
          .forEach(astAliasDecl -> addToStateBlock(root, astAliasDecl));

      // remaining entries are y_index update entries
      // these statements must be printed at the end of the dynamics function
      ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

      for (final String line:stateVectorLines) {
        final ASTAssignment yVarAssignment = converter2NESTML.convertStringToAssignment(line);

        // Depends on the SPL grammar structure
        addAssignmentToDynamics(astBodyDecorator, yVarAssignment);
      }
      // add extra handling of the y0 variable
      // print resulted model to the file
      // TODO
      final NeuronSymbol neuronSymbol = (NeuronSymbol)
          root.getNeurons().get(0).getSymbol().get();

      if (!neuronSymbol.getSpikeBuffers().isEmpty()) {
        final VariableSymbol spikeBuffer = neuronSymbol.getSpikeBuffers().get(0);
        final ASTAssignment pscUpdateStep = converter2NESTML
            .convertStringToAssignment("y1 = " + spikeBuffer.getName() + ".getSum(t)");
        addAssignmentToDynamics(astBodyDecorator, pscUpdateStep);
      }
      return root;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot solveODE stateVector output from the SymPy solver", e);
    }
  }

  public ASTNESTMLCompilationUnit replaceODE(
      final ASTNESTMLCompilationUnit root,
      final Path updateStepFile) {
    final ASTAssignment stateUpdate = converter2NESTML.convertToAssignment(updateStepFile);

    ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

    final ODECollector odeCollector = new ODECollector();
    odeCollector.startVisitor(astBodyDecorator.getDynamics().get(0));
    if (!odeCollector.getFoundOde().isPresent()) {
      Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
      return root;
    }

    final Optional<ASTNode> parent = ASTNodes.getParent(odeCollector.getFoundOde().get(), root);
    checkState(parent.isPresent());
    checkState(parent.get() instanceof ASTSmall_Stmt);

    final ASTSmall_Stmt castedParent = (ASTSmall_Stmt) parent.get();
    castedParent.setAssignment(stateUpdate);

    return root;
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
      if (getQualifiedName(astFunctionCall.getQualifiedName().getParts()).equals("integrate")) {
        foundOde = Optional.of(astFunctionCall);
      }
    }

    public Optional<ASTFunctionCall> getFoundOde() {
      return foundOde;
    }

  }

  private void addAssignmentToDynamics(ASTBodyDecorator astBodyDecorator,
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
  private void addToInternalBlock(
      final ASTNESTMLCompilationUnit root,
      final ASTAliasDecl declaration) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    astBodyDecorator.addToInternalBlock(declaration);
  }

  private void addToStateBlock(
      final ASTNESTMLCompilationUnit root,
      final ASTAliasDecl declaration) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    astBodyDecorator.addToStateBlock(declaration);
  }

}
