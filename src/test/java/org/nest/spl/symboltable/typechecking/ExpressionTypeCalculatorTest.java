/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import org.junit.Assert;
import org.junit.Test;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Test the functioning of the expression pretty printer
 *
 * @author plotnikov
 */
public class ExpressionTypeCalculatorTest {

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  public static final String TEST_MODEL = "src/test/resources/org/nest/spl/symboltable"
      + "/mathExpressions.simple";

  @Test
  public void testTypeCalculation() throws IOException {
    final SPLParser p = new SPLParser();
    final Optional<ASTSPLFile> root = p.parse(TEST_MODEL);
    assertTrue(root.isPresent());

    final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    scopeCreator.runSymbolTableCreator(root.get());

    final ExpressionTypeCalculator calculator = new ExpressionTypeCalculator();

    // Retrieves line: b = 1.0
    final Optional<ASTDeclaration> bDeclaration = root.get()
        .getBlock().getStmts().get(1)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getDeclaration();
    assertTrue(bDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfB = calculator.computeType(bDeclaration.get().getExpr().get());
    assertTrue(typeOfB.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), typeOfB.getLeft().get());


    // Retrieves line: c = 1
    final Optional<ASTAssignment> cDeclaration = root.get()
        .getBlock().getStmts().get(2)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(cDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfC = calculator.computeType(cDeclaration.get().getExpr());
    assertTrue(typeOfC.isLeft());
    Assert.assertEquals(PredefinedTypes.getIntegerType(), typeOfC.getLeft().get());


    // Retrieves line: d = "test"
    final Optional<ASTAssignment> dDeclaration = root.get()
        .getBlock().getStmts().get(3)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(dDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfD = calculator.computeType(dDeclaration.get().getExpr());
    assertTrue(typeOfD.isLeft());
    Assert.assertEquals(PredefinedTypes.getStringType(), typeOfD.getLeft().get());


    // Retrieves line: e = 1 + 1
    final Optional<ASTAssignment> eDeclaration = root.get()
        .getBlock().getStmts().get(4)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(dDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfE = calculator.computeType(eDeclaration.get().getExpr());
    assertTrue(typeOfE.isLeft());
    Assert.assertEquals(PredefinedTypes.getIntegerType(), typeOfE.getLeft().get());


    // Retrieves line: f = 1 + 1.0
    final Optional<ASTAssignment> fDeclaration = root.get()
        .getBlock().getStmts().get(5)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(dDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfF = calculator.computeType(fDeclaration.get().getExpr());
    assertTrue(typeOfF.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), typeOfF.getLeft().get());


    // Retrieves line: f = 1.0 + 1
    final Optional<ASTAssignment> gDeclaration = root.get()
        .getBlock().getStmts().get(6)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(dDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfG = calculator.computeType(gDeclaration.get().getExpr());
    assertTrue(typeOfG.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), typeOfG.getLeft().get());


    // Retrieves line: f = 1.0 + 1
    final Optional<ASTAssignment> hDeclaration = root.get()
        .getBlock().getStmts().get(7)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(dDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfH = calculator.computeType(hDeclaration.get().getExpr());
    assertTrue(typeOfH.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), typeOfH.getLeft().get());


    // Retrieves line: i = ~1
    final Optional<ASTAssignment> iDeclaration = root.get()
        .getBlock().getStmts().get(8)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(iDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfI = calculator.computeType(iDeclaration.get().getExpr());
    assertTrue(typeOfI.isLeft());
    Assert.assertEquals(PredefinedTypes.getIntegerType(), typeOfI.getLeft().get());


    // Retrieves line: j = ~b, b is a string
    final Optional<ASTAssignment> jDeclaration = root.get()
        .getBlock().getStmts().get(10)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(jDeclaration.isPresent());

    final Either<TypeSymbol, String> jType = calculator.computeType(jDeclaration.get().getExpr());
    assertTrue(jType.isRight());
    // Retrieves line: l = 1 ** 2.5
    final Optional<ASTAssignment> kDeclaration = root.get()
        .getBlock().getStmts().get(11)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(iDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfK = calculator.computeType(kDeclaration.get().getExpr());
    assertTrue(typeOfK.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), typeOfK.getLeft().get());

    // Retrieves line: m = 1 ** d, b is a string
    final Optional<ASTAssignment> mDeclaration = root.get()
        .getBlock().getStmts().get(12)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(mDeclaration.isPresent());

    final Either<TypeSymbol, String> mType = calculator.computeType(mDeclaration.get().getExpr());
    assertTrue(mType.isRight());

    // Retrieves line: o = 1 - 1
    final Optional<ASTAssignment> oDeclaration = root.get().
        getBlock().getStmts().get(13)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(oDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfO = calculator.computeType(oDeclaration.get().getExpr());
    assertTrue(typeOfO.isLeft());
    Assert.assertEquals(PredefinedTypes.getIntegerType(), typeOfO.getLeft().get());

    // Retrieves line: p = 1 - 1.0
    final Optional<ASTAssignment> pDeclaration = root.get()
        .getBlock().getStmts().get(14)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(pDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfP = calculator.computeType(pDeclaration.get().getExpr());
    assertTrue(typeOfP.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), typeOfP.getLeft().get());

    // Retrieves line: r = 1 - d, b is a string
    final Optional<ASTAssignment> rDeclaration = root.get()
        .getBlock().getStmts().get(15)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(rDeclaration.isPresent());

    final Either<TypeSymbol, String> rType = calculator.computeType(rDeclaration.get().getExpr());
    assertTrue(rType.isRight());
    // Retrieves line: t = true
    final Optional<ASTAssignment> sDeclaration = root.get()
        .getBlock().getStmts().get(16)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(sDeclaration.isPresent());

    final Either<TypeSymbol, String> typeOfS = calculator.computeType(sDeclaration.get().getExpr());
    assertTrue(typeOfS.isLeft());
    Assert.assertEquals(PredefinedTypes.getBooleanType(), typeOfS.getLeft().get());

    final Optional<ASTDeclaration> P11exAST = root.get()
        .getBlock().getStmts().get(19)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getDeclaration();
    assertTrue(P11exAST.isPresent());

    final Either<TypeSymbol, String> P11exType = calculator.computeType(P11exAST.get().getExpr().get());
    assertTrue(P11exType.isLeft());
    Assert.assertEquals(PredefinedTypes.getRealType(), P11exType.getLeft().get());
    // find ast by name
  }


}
