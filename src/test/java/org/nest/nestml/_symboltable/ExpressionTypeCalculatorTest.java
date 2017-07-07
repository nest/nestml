/*
 * ExpressionTypeCalculatorTest.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.nestml._symboltable;

import org.junit.Assert;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTVariable;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.*;

/**
 * Test the functioning of the expression pretty printer
 *
 * @author plotnikov
 */
public class ExpressionTypeCalculatorTest extends ModelbasedTest {
  private static final String TEST_POSITIVE_MODEL = "src/test/resources/org/nest/nestml/_cocos/valid"
                                                    + "/mathExpressions.nestml";
  private static final String TEST_NEGATIVE_MODEL = "src/test/resources/org/nest/nestml/_cocos/invalid"
                                                    + "/mathExpressions.nestml";

  @Test
  public void testTypeCalculation() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> root = parser.parse(TEST_POSITIVE_MODEL);
    assertTrue(root.isPresent());

    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator();
    scopeCreator.runSymbolTableCreator(root.get());
    final List<ASTDeclaration> declarations = AstUtils.getAll(root.get(), ASTDeclaration.class);

    // b real = 1.0
    final Either<TypeSymbol, String> typeOfB = getByName(declarations, "b").getExpr().get().getType();
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
        getByName(declarations, "gg").getExpr().get().getType();
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
        getByName(declarations, "m1").getExpr().get().getType();
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
    final Optional<ASTNESTMLCompilationUnit> root = parser.parse(TEST_NEGATIVE_MODEL);
    assertTrue(root.isPresent());

    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator();
    scopeCreator.runSymbolTableCreator(root.get());
    final List<ASTDeclaration> declarations = AstUtils.getAll(root.get(), ASTDeclaration.class);

    // a real = ((( 1.0 | (-3+6%2) & ~(0x4fa) | 0x23 ^ 12) >> 2) << 2)
    final Either<TypeSymbol, String> typeOfA =
        getByName(declarations, "a").getExpr().get().getType();
    assertTrue(typeOfA.isError());

    // k integer = ~1.0
    final Either<TypeSymbol, String> typeOfK =
        getByName(declarations, "kk").getExpr().get().getType();
    assertTrue(typeOfK.isError());

    // m real = 1 ** "a"
    final Either<TypeSymbol, String> typeOfM =
        getByName(declarations, "a").getExpr().get().getType();
    assertTrue(typeOfM.isError());

    // n boolean = not 1
    assertInvalidType("n", declarations);

    //o1 real = 12? 13:14
    assertInvalidType("o1", declarations);

    //o2 real = true?13:"test"
    assertInvalidType("o2", declarations);

  }

  private void assertInvalidType(final String variableName, List<ASTDeclaration> declarations) {
    final Either<TypeSymbol, String> type = getByName(declarations, variableName).getExpr().get().getType();
    assertTrue(type.isError());
  }

  private ASTDeclaration getByName(
      final List<ASTDeclaration> declarations,
      final String variableName) {

    for (final ASTDeclaration astDeclaration:declarations) {
      for (final ASTVariable astVariable:astDeclaration.getVars()) {
        if (astVariable.toString().equals(variableName)) {
          return astDeclaration;
        }
      }
    }

    assertTrue("No declration with this variable was found.", false);
    throw new RuntimeException();
  }

}
