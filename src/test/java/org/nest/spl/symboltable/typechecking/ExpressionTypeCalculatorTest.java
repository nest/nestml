/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import org.junit.Assert;
import org.junit.Test;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTUtils;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * Test the functioning of the expression pretty printer
 *
 * @author plotnikov
 */
public class ExpressionTypeCalculatorTest {
  private final SPLParser splParser = new SPLParser();
  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String TEST_POSITIVE_MODEL = "src/test/resources/org/nest/spl/_cocos/valid"
      + "/mathExpressions.simple";
  private static final String TEST_NEGATIVE_MODEL = "src/test/resources/org/nest/spl/_cocos/invalid"
      + "/mathExpressions.simple";

  private final ExpressionTypeCalculator calculator = new ExpressionTypeCalculator();

  @Test
  public void testTypeCalculation() throws IOException {
    final Optional<ASTSPLFile> root = splParser.parse(TEST_POSITIVE_MODEL);
    assertTrue(root.isPresent());

    final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    scopeCreator.runSymbolTableCreator(root.get());
    final List<ASTDeclaration> declarations = ASTUtils.getAll(root.get(), ASTDeclaration.class);

    // b real = 1.0
    final Either<TypeSymbol, String> typeOfB = calculator.computeType(
        getByName(declarations, "b").getExpr().get());
    assertTrue(typeOfB.isValue());
    Assert.assertEquals(getRealType(), typeOfB.getValue());

    // Retrieves line: c = 1
    final Either<TypeSymbol, String> typeOfC = calculator.computeType(
        getByName(declarations, "c").getExpr().get());
    assertTrue(typeOfC.isValue());
    Assert.assertEquals(getIntegerType(), typeOfC.getValue());

    // Retrieves line: d = "test"
    final Either<TypeSymbol, String> typeOfD = calculator.computeType(
        getByName(declarations, "d").getExpr().get());
    assertTrue(typeOfD.isValue());
    Assert.assertEquals(getStringType(), typeOfD.getValue());

    // Retrieves line: e = 1 + 1
    final Either<TypeSymbol, String> typeOfE = calculator.computeType(
        getByName(declarations, "c").getExpr().get());
    assertTrue(typeOfE.isValue());
    Assert.assertEquals(getIntegerType(), typeOfE.getValue());

    // Retrieves line: f = 1 + 1.0
    final Either<TypeSymbol, String> typeOfF = calculator.computeType(
        getByName(declarations, "f").getExpr().get());
    assertTrue(typeOfF.isValue());
    Assert.assertEquals(getRealType(), typeOfF.getValue());

    // Retrieves line: g = 1.0 + 1
    final Either<TypeSymbol, String> typeOfG = calculator.computeType(
        getByName(declarations, "g").getExpr().get());
    assertTrue(typeOfG.isValue());
    Assert.assertEquals(getRealType(), typeOfG.getValue());

    // Retrieves line: h real = 1 + 1 + 1 + 1 + 1.0
    final Either<TypeSymbol, String> typeOfH = calculator.computeType(
        getByName(declarations, "h").getExpr().get());
    assertTrue(typeOfH.isValue());
    Assert.assertEquals(getRealType(), typeOfH.getValue());

    // l real = 1 ** 2.5
    final Either<TypeSymbol, String> typeOfL = calculator.computeType(
        getByName(declarations, "l").getExpr().get());
    assertTrue(typeOfL.isValue());
    Assert.assertEquals(getRealType(), typeOfL.getValue());

    // Retrieves line: i = ~1 l is integer
    final Either<TypeSymbol, String> typeOfI = calculator.computeType(
        getByName(declarations, "i").getExpr().get());
    assertTrue(typeOfG.isValue());
    Assert.assertEquals(getIntegerType(), typeOfI.getValue());

    // Retrieves line: P11ex real = pow(1.0, 1.0)
    final Either<TypeSymbol, String> typeOfP11ex = calculator.computeType(
        getByName(declarations, "P11ex").getExpr().get());
    assertTrue(typeOfP11ex.isValue());
    Assert.assertEquals(getRealType(), typeOfP11ex.getValue());

    // Retrieves line: tmp string = ("")
    final Either<TypeSymbol, String> typeOfTmp = calculator.computeType(
        getByName(declarations, "tmp").getExpr().get());
    assertTrue(typeOfTmp.isValue());
    Assert.assertEquals(getStringType(), typeOfTmp.getValue());

    // Retrieves line: m boolean = true and l != 0.0
    final Either<TypeSymbol, String> typeOfM = calculator.computeType(
        getByName(declarations, "m").getExpr().get());
    assertTrue(typeOfM.isValue());
    Assert.assertEquals(getBooleanType(), typeOfM.getValue());

    // n boolean = not true
    assertType("n", declarations, getBooleanType());
  }

  private void assertType(final String variableName, List<ASTDeclaration> declarations, final TypeSymbol expectedType) {
    final Either<TypeSymbol, String> type = calculator.computeType
        (getByName(declarations, variableName).getExpr().get());
    assertTrue(type.isValue());
    Assert.assertEquals(expectedType, type.getValue());
  }


  @Test
  public void testNegativeExamples() throws IOException {
    final Optional<ASTSPLFile> root = splParser.parse(TEST_NEGATIVE_MODEL);
    assertTrue(root.isPresent());

    final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    scopeCreator.runSymbolTableCreator(root.get());
    final ExpressionTypeCalculator calculator = new ExpressionTypeCalculator();
    final List<ASTDeclaration> declarations = ASTUtils.getAll(root.get(), ASTDeclaration.class);

    // a real = ((( 1.0 | (-3+6%2) & ~(0x4fa) | 0x23 ^ 12) >> 2) << 2)
    final Either<TypeSymbol, String> typeOfA = calculator.computeType(
        getByName(declarations, "a").getExpr().get());
    assertTrue(typeOfA.isError());

    // k integer = ~1.0
    final Either<TypeSymbol, String> typeOfK = calculator.computeType(
        getByName(declarations, "k").getExpr().get());
    assertTrue(typeOfK.isError());

    // m real = 1 ** "a"
    final Either<TypeSymbol, String> typeOfM = calculator.computeType(
        getByName(declarations, "a").getExpr().get());
    assertTrue(typeOfM.isError());

    // n boolean = not 1
    assertInvaidType("n", declarations);


  }

  private void assertInvaidType(final String variableName, List<ASTDeclaration> declarations) {
    final Either<TypeSymbol, String> type = calculator.computeType(getByName(declarations, variableName).getExpr().get());
    assertTrue(type.isError());
  }

  private ASTDeclaration getByName(
      final List<ASTDeclaration> declarations,
      final String variableName) {
    final Optional<ASTDeclaration> declaration = declarations.stream().
        filter(e -> e.getVars().contains(variableName))
        .findFirst();
    assertTrue(declaration.isPresent());
    return declaration.get();
  }

}
