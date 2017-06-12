/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Before;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NestmlCoCosManager;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTSmall_Stmt;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.spl.prettyprinter.SPLPrettyPrinter;
import org.nest.spl.prettyprinter.SPLPrettyPrinterFactory;

import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.NESTMLRootCreator.getAstRoot;

/**
 * Checks that the SI unit checking works stable.
 *
 * @author traeder, plotnikov
 */
public class UnitsTest extends ModelbasedTest {
  AssignmentTestVisitor assignmentTestVisitor = new AssignmentTestVisitor();

  class AssignmentTestVisitor implements NESTMLVisitor{

    public void visit(ASTSmall_Stmt astSmall_stmt){
      SPLPrettyPrinter printer = SPLPrettyPrinterFactory.createDefaultPrettyPrinter();
      if(astSmall_stmt.assignmentIsPresent() || astSmall_stmt.declarationIsPresent()){
        printer.print(astSmall_stmt);
        Log.error("assignment: "+ printer.result().substring(0,printer.result().length()-1) +" line: "+astSmall_stmt.get_SourcePositionStart().getLine());


      }

    }
  }

  @Before
  public void clearLog() {
    Log.enableFailQuick(false);
    Log.getFindings().clear();
  }

  @Test
  public void test_unit_assignments(){
    final NestmlCoCosManager completeChecker = new NestmlCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "src/test/resources/org/nest/units/assignmentTest/validAssignments.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());

    List<Finding> findings = completeChecker.analyzeModel(validRoot.get());
    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);

    long warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(10, warningsFound);

    //some semantic tests on addition of units:
    validRoot.get().accept(assignmentTestVisitor);


    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        "src/test/resources/org/nest/units/assignmentTest/invalidAssignments.nestml", TEST_MODEL_PATH);

    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    findings = completeChecker.analyzeModel(invalidRoot.get());
    errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(7, errorsFound);

    warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(15, warningsFound);
  }

  @Test
  public void test_unit_expressions(){
    final NestmlCoCosManager completeChecker = new NestmlCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "src/test/resources/org/nest/units/expressionTest/validExpressions.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());

    List<Finding> findings = completeChecker.analyzeModel(validRoot.get());
    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);

    long warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(19, warningsFound);

    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        "src/test/resources/org/nest/units/expressionTest/invalidExpressions.nestml", TEST_MODEL_PATH);

    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    findings = completeChecker.analyzeModel(invalidRoot.get());
    errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(18, errorsFound);

    warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(15, warningsFound);
  }

  @Test
  public void test_unit_ODEs(){
    final NestmlCoCosManager completeChecker = new NestmlCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "src/test/resources/org/nest/units/ODETest/validODEs.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());

    List<Finding> findings = completeChecker.analyzeModel(validRoot.get());
    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);

    long warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(0, warningsFound);

    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        "src/test/resources/org/nest/units/ODETest/invalidODEs.nestml", TEST_MODEL_PATH);

    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    findings = completeChecker.analyzeModel(invalidRoot.get());
    errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);

    warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(0, warningsFound);
  }

  @Test
  public void test_unit_declarations(){
    final NestmlCoCosManager completeChecker = new NestmlCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "src/test/resources/org/nest/units/declarationTest/validDeclarations.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());

    List<Finding> findings = completeChecker.analyzeModel(validRoot.get());
    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);

    long warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(0, warningsFound);

    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        "src/test/resources/org/nest/units/declarationTest/invalidDeclarations.nestml", TEST_MODEL_PATH);

    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    findings = completeChecker.analyzeModel(invalidRoot.get());
    errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);

    warningsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(1, warningsFound);
  }


  @Test
  public void test_iaf_cond_alpha() {
    final NestmlCoCosManager completeChecker = new NestmlCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "models/iaf_cond_alpha.nestml", TEST_MODEL_PATH);
    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    final List<Finding> findings = completeChecker.analyzeModel(validRoot.get());

    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();
    assertEquals(0, errorsFound);
  }

}
