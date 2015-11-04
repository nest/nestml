/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import org.apache.commons.io.FileUtils;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLVisitor;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;
import org.nest.utils.ASTNodes;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;

/**
 * Manages the overall script generation and evaluation of the generated scripts
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  final SymPy2NESTMLConverter converter2NESTML = new SymPy2NESTMLConverter();

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  public void addP00(
      final ASTNESTMLCompilationUnit root,
      final String pathToP00File,
      final String outputModelFile) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAlias(pathToP00File);

    addToInternalBlock(root, p00Declaration);

    printModelToFile(root, outputModelFile);
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  public void addPSCInitialValue(
      final ASTNESTMLCompilationUnit root,
      final String pathPSCInitialValueFile,
      final String outputModelFile) {

    final ASTAliasDecl pscInitialValue = converter2NESTML.convertToAlias(pathPSCInitialValueFile);

    addToInternalBlock(root, pscInitialValue);

    printModelToFile(root, outputModelFile);
  }

  public void addStateVariablesAndUpdateStatements(
      final ASTNESTMLCompilationUnit root,
      final String stateVectorFile,
      final String outputModelFile) {
    try {
      final List<String> stateVectorLines = Files.lines(Paths.get(stateVectorFile))
              .collect(Collectors.toList());

      checkState(stateVectorLines.size() > 0, "False stateVector.mat format. Check SymPy solver.");

      // First entry is the number of variables
      final Integer stateVariablesNumber = Integer.valueOf(stateVectorLines.get(0));
      // oder y values + oder value itself
      checkState(stateVectorLines.size() == stateVariablesNumber + 1,
          "False stateVector.mat format. Check SymPy solver.");

      final List<String> stateVariableDeclarations = Lists.newArrayList();
      stateVariableDeclarations.add("y0 real");
      for (int i = 1; i <= stateVariablesNumber; ++i) {
        stateVariableDeclarations.add("y"+ i + " real");
      }
      stateVariableDeclarations.stream()
          .map(converter2NESTML::convertStringToAlias)
          .forEach(astAliasDecl -> addToStateBlock(root, astAliasDecl));

      // remaining entries are y_index update entries
      // these statements must be printed at the end of the dynamics function
      ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

      for (int i = 1; i <= stateVariablesNumber; ++i) {
        final ASTAssignment yVarAssignment = converter2NESTML.convertStringToAssignment(stateVectorLines.get(i));

        // Depends on the SPL grammar structure
        addAssignmentToDynamics(astBodyDecorator, yVarAssignment);
      }
      // add extra handling of the y0 variable
      // print resulted model to the file
      final NESTMLNeuronSymbol nestmlNeuronSymbol = (NESTMLNeuronSymbol)
          root.getNeurons().get(0).getSymbol().get();

      if (!nestmlNeuronSymbol.getCurrentBuffers().isEmpty()) {
        final NESTMLVariableSymbol currentBuffer = nestmlNeuronSymbol.getCurrentBuffers().get(0);
        final ASTAssignment y0Assignment = converter2NESTML
            .convertStringToAssignment("y0 = " + currentBuffer.getName() + ".getSum(t)");
        addAssignmentToDynamics(astBodyDecorator, y0Assignment);
      }

      printModelToFile(root, outputModelFile);
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot process stateVector output from the SymPy solver", e);
    }
  }

  private class ODECollector implements NESTMLVisitor {
    private Optional<ASTOdeDeclaration> foundOde = Optional.empty();

    public void startVisitor(ASTNESTMLNode node) {
      node.accept(this);
    }

    @Override
    public void visit(final ASTOdeDeclaration astOdeDeclaration) {
      foundOde = Optional.of(astOdeDeclaration);
    }

    public Optional<ASTOdeDeclaration> getFoundOde() {
      return foundOde;
    }

  }

  public void replaceODE(
      final ASTNESTMLCompilationUnit root,
      final String updateStepFile,
      final String outputModelFile) {
    final ASTAssignment stateUpdate = converter2NESTML.convertToAssignment(updateStepFile);

    ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    final ODECollector odeCollector = new ODECollector();
    odeCollector.startVisitor(astBodyDecorator.getDynamics().get(0));
    checkState(odeCollector.getFoundOde().isPresent());

    final Optional<ASTNode> parent = ASTNodes.getParent(odeCollector.getFoundOde().get(), root);
    checkState(parent.isPresent());
    checkState(parent.get() instanceof ASTSmall_Stmt);
    final ASTSmall_Stmt castedParent = (ASTSmall_Stmt) parent.get();
    castedParent.setAssignment(stateUpdate);

    printModelToFile(root, outputModelFile);
  }

  private void addAssignmentToDynamics(ASTBodyDecorator astBodyDecorator,
      ASTAssignment yVarAssignment) {
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    final ASTSimple_Stmt astSimpleStmt = SPLNodeFactory.createASTSimple_Stmt();
    final ASTSmall_StmtList astSmallStmts = SPLNodeFactory.createASTSmall_StmtList();
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();

    astStmt.setSimple_Stmt(astSimpleStmt);
    astSmallStmts.add(astSmall_stmt);
    astSimpleStmt.setSmall_Stmts(astSmallStmts);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(yVarAssignment);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }

  // TODO: replace it with return root call
  private void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputModelFile) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputModelFile);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
     throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputModelFile, e);
    }
  }

  // TODO do I need functions?
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
