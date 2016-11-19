/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import org.junit.Assert;
import org.junit.Test;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

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

  @Test
  public void testTypeCalculation() throws IOException {
    final Optional<ASTSPLFile> root = splParser.parse(TEST_POSITIVE_MODEL);
    assertTrue(root.isPresent());

    final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    scopeCreator.runSymbolTableCreator(root.get());
    final List<ASTDeclaration> declarations = AstUtils.getAll(root.get(), ASTDeclaration.class);

    // b real = 1.0
    final Either<TypeSymbol, String> typeOfB =
        getByName(declarations, "b").getExpr().get().getType();
    assertTrue(typeOfB.isValue());
    Assert.assertEquals(getRealType(), typeOfB.getValue());

    // Retrieves line: c = 1
    final Either<TypeSymbol, String> typeOfC =
        getByName(declarations, "c").getExpr().get().getType();
    assertTrue(typeOfC.isValue());
    Assert.assertEquals(getIntegerType(), typeOfC.getValue());

    // Retrieves line: d = "test"
    final Either<TypeSymbol, String> typeOfD =
        getByName(declarations, "d").getExpr().get().getType();
    assertTrue(typeOfD.isValue());
    Assert.assertEquals(getStringType(), typeOfD.getValue());

    // Retrieves line: e = 1 + 1
    final Either<TypeSymbol, String> typeOfE =
        getByName(declarations, "c").getExpr().get().getType();
    assertTrue(typeOfE.isValue());
    Assert.assertEquals(getIntegerType(), typeOfE.getValue());

    // Retrieves line: f = 1 + 1.0
    final Either<TypeSymbol, String> typeOfF =
        getByName(declarations, "f").getExpr().get().getType();
    assertTrue(typeOfF.isValue());
    Assert.assertEquals(getRealType(), typeOfF.getValue());

    // Retrieves line: g = 1.0 + 1
    final Either<TypeSymbol, String> typeOfG =
        getByName(declarations, "g").getExpr().get().getType();
    assertTrue(typeOfG.isValue());
    Assert.assertEquals(getRealType(), typeOfG.getValue());

    // Retrieves line: h real = 1 + 1 + 1 + 1 + 1.0
    final Either<TypeSymbol, String> typeOfH =
        getByName(declarations, "h").getExpr().get().getType();
    assertTrue(typeOfH.isValue());
    Assert.assertEquals(getRealType(), typeOfH.getValue());

    // l real = 1 ** 2.5
    final Either<TypeSymbol, String> typeOfL =
        getByName(declarations, "l").getExpr().get().getType();
    assertTrue(typeOfL.isValue());
    Assert.assertEquals(getRealType(), typeOfL.getValue());

    // Retrieves line: i = ~1 l is integer
    final Either<TypeSymbol, String> typeOfI =
        getByName(declarations, "i").getExpr().get().getType();
    assertTrue(typeOfG.isValue());
    Assert.assertEquals(getIntegerType(), typeOfI.getValue());

    // Retrieves line: P11ex real = pow(1.0, 1.0)
    final Either<TypeSymbol, String> typeOfP11ex =
        getByName(declarations, "P11ex").getExpr().get().getType();
    assertTrue(typeOfP11ex.isValue());
    Assert.assertEquals(getRealType(), typeOfP11ex.getValue());

    // Retrieves line: tmp string = ("")
    final Either<TypeSymbol, String> typeOfTmp =
        getByName(declarations, "tmp").getExpr().get().getType();
    assertTrue(typeOfTmp.isValue());
    Assert.assertEquals(getStringType(), typeOfTmp.getValue());

    // Retrieves line: m boolean = true and l != 0.0
    final Either<TypeSymbol, String> typeOfM =
        getByName(declarations, "m").getExpr().get().getType();
    assertTrue(typeOfM.isValue());
    Assert.assertEquals(getBooleanType(), typeOfM.getValue());

    // n boolean = not true
    assertType("n", declarations, getBooleanType());

    // o1 real = true? 13:14
    assertType("o1", declarations, getIntegerType());

    // o2 string = true?"test1":"test"
    assertType("o2", declarations, getStringType());
  }

  private void assertType(final String variableName, List<ASTDeclaration> declarations, final TypeSymbol expectedType) {
    final Either<TypeSymbol, String> type =
        getByName(declarations, variableName).getExpr().get().getType();
    assertTrue(type.isValue());
    Assert.assertEquals(expectedType, type.getValue());
  }


  @Test
  public void testNegativeExamples() throws IOException {
    final Optional<ASTSPLFile> root = splParser.parse(TEST_NEGATIVE_MODEL);
    assertTrue(root.isPresent());

    final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    scopeCreator.runSymbolTableCreator(root.get());
    final List<ASTDeclaration> declarations = AstUtils.getAll(root.get(), ASTDeclaration.class);

    // a real = ((( 1.0 | (-3+6%2) & ~(0x4fa) | 0x23 ^ 12) >> 2) << 2)
    final Either<TypeSymbol, String> typeOfA =
        getByName(declarations, "a").getExpr().get().getType();
    assertTrue(typeOfA.isError());

    // k integer = ~1.0
    final Either<TypeSymbol, String> typeOfK =
        getByName(declarations, "k").getExpr().get().getType();
    assertTrue(typeOfK.isError());

    // m real = 1 ** "a"
    final Either<TypeSymbol, String> typeOfM =
        getByName(declarations, "a").getExpr().get().getType();
    assertTrue(typeOfM.isError());

    // n boolean = not 1
    assertInvaidType("n", declarations);

    //o1 real = 12? 13:14
    assertInvaidType("o1", declarations);

    //o2 real = true?13:"test"
    assertInvaidType("o2", declarations);

  }

  private void assertInvaidType(final String variableName, List<ASTDeclaration> declarations) {
    final Either<TypeSymbol, String> type = getByName(declarations, variableName).getExpr().get().getType();
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
