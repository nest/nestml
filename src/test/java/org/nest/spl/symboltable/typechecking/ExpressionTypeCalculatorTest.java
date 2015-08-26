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
import org.nest.spl._parser.SPLFileMCParser;
import org.nest.spl._parser.SPLParserFactory;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

/**
 * Test the functioning of the expression pretty printer
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class ExpressionTypeCalculatorTest {

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  public static final String TEST_MODEL = "src/test/resources/org/nest/spl/symboltable/mathExpressions.simple";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void testTypeCalculation() throws IOException {
    final SPLFileMCParser p = SPLParserFactory.createSPLFileMCParser();
    final Optional<ASTSPLFile> root = p.parse(TEST_MODEL);
    assertTrue(root.isPresent());

    final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH, typesFactory);
    scopeCreator.runSymbolTableCreator(root.get());

    final ExpressionTypeCalculator calculator = new ExpressionTypeCalculator(typesFactory);

    // Retrieves line: b = 1.0
    final Optional<ASTDeclaration> bDeclaration = root.get()
        .getBlock().getStmts().get(1)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getDeclaration();
    Assert.assertTrue(bDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfB = calculator.computeType(bDeclaration.get().getExpr().get());
    Assert.assertNotNull(typeOfB);
    Assert.assertEquals(typesFactory.getRealType(), typeOfB);

    // Retrieves line: c = 1
    final Optional<ASTAssignment> cDeclaration = root.get()
        .getBlock().getStmts().get(2)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(cDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfC = calculator.computeType(cDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfC);
    Assert.assertEquals(typesFactory.getIntegerType(), typeOfC);

    // Retrieves line: d = "test"
    final Optional<ASTAssignment> dDeclaration = root.get()
        .getBlock().getStmts().get(3)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(dDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfD = calculator.computeType(dDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfD);
    Assert.assertEquals(typesFactory.getStringType(), typeOfD);

    // Retrieves line: e = 1 + 1
    final Optional<ASTAssignment> eDeclaration = root.get()
        .getBlock().getStmts().get(4)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(dDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfE = calculator.computeType(eDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfE);
    Assert.assertEquals(typesFactory.getIntegerType(), typeOfE);

    // Retrieves line: f = 1 + 1.0
    final Optional<ASTAssignment> fDeclaration = root.get()
        .getBlock().getStmts().get(5)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(dDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfF = calculator.computeType(fDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfF);
    Assert.assertEquals(typesFactory.getRealType(), typeOfF);

    // Retrieves line: f = 1.0 + 1
    final Optional<ASTAssignment> gDeclaration = root.get()
        .getBlock().getStmts().get(6)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(dDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfG = calculator.computeType(gDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfG);
    Assert.assertEquals(typesFactory.getRealType(), typeOfG);

    // Retrieves line: f = 1.0 + 1
    final Optional<ASTAssignment> hDeclaration = root.get()
        .getBlock().getStmts().get(7)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(dDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfH = calculator.computeType(hDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfH);
    Assert.assertEquals(typesFactory.getRealType(), typeOfH);

    // Retrieves line: i = ~1
    final Optional<ASTAssignment> iDeclaration = root.get()
        .getBlock().getStmts().get(8)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(iDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfI = calculator.computeType(iDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfI);
    Assert.assertEquals(typesFactory.getIntegerType(), typeOfI);

    // Retrieves line: j = ~b, b is a string
    final Optional<ASTAssignment> jDeclaration = root.get()
        .getBlock().getStmts().get(10)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(jDeclaration.isPresent());

    try {
      calculator.computeType(jDeclaration.get().getExpr());
      fail();
    }
    catch (RuntimeException e) {
      // expects an type computation exception
    }

    // Retrieves line: l = 1 ** 2.5
    final Optional<ASTAssignment> kDeclaration = root.get()
        .getBlock().getStmts().get(11)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(iDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfK = calculator.computeType(kDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfK);
    Assert.assertEquals(typesFactory.getRealType(), typeOfK);

    // Retrieves line: m = 1 ** d, b is a string
    final Optional<ASTAssignment> mDeclaration = root.get()
        .getBlock().getStmts().get(12)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(mDeclaration.isPresent());

    try {
      calculator.computeType(mDeclaration.get().getExpr());
      fail();
    }
    catch (RuntimeException e) {
      // expects an type computation exception
    }

    // Retrieves line: o = 1 - 1
    final Optional<ASTAssignment> oDeclaration = root.get().
        getBlock().getStmts().get(13)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(oDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfO = calculator.computeType(oDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfO);
    Assert.assertEquals(typesFactory.getIntegerType(), typeOfO);

    // Retrieves line: p = 1 - 1.0
    final Optional<ASTAssignment> pDeclaration = root.get()
        .getBlock().getStmts().get(14)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(pDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfP = calculator.computeType(pDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfP);
    Assert.assertEquals(typesFactory.getRealType(), typeOfP);

    // Retrieves line: r = 1 - d, b is a string
    final Optional<ASTAssignment> rDeclaration = root.get()
        .getBlock().getStmts().get(15)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(rDeclaration.isPresent());

    try {
      calculator.computeType(rDeclaration.get().getExpr());
      fail();
    }
    catch (RuntimeException e) {
      // expects an type computation exception
    }

    // Retrieves line: t = true
    final Optional<ASTAssignment> sDeclaration = root.get()
        .getBlock().getStmts().get(16)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    Assert.assertTrue(sDeclaration.isPresent());

    final NESTMLTypeSymbol typeOfS = calculator.computeType(sDeclaration.get().getExpr());
    Assert.assertNotNull(typeOfS);
    Assert.assertEquals(typesFactory.getBooleanType(), typeOfS);

    final Optional<ASTDeclaration> P11exAST = root.get()
        .getBlock().getStmts().get(19)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getDeclaration();
    Assert.assertTrue(P11exAST.isPresent());

    final NESTMLTypeSymbol P11exType = calculator.computeType(P11exAST.get().getExpr().get());
    Assert.assertNotNull(P11exType);
    Assert.assertEquals(typesFactory.getRealType(), P11exType);

  }


}
