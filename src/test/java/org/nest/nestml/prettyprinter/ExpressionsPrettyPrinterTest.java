/*
 * ExpressionsPrettyPrinterTest.java
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
package org.nest.nestml.prettyprinter;

import com.google.common.io.Files;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.io.StringReader;
import java.nio.charset.Charset;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests prettyprinter on the most available models in test resources.
 *
 * @author plotnikov
 */
public class ExpressionsPrettyPrinterTest extends ModelbasedTest {
  private final ExpressionsPrettyPrinter expressionsPrettyPrinter = new ExpressionsPrettyPrinter();
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private final NESTMLParser nestmlParser = new NESTMLParser(Paths.get(TEST_MODEL_PATH));

  @Test
  public void testThatPrettyPrinterProducesParsableOutput() throws IOException {

    final Optional<ASTNESTMLCompilationUnit> root = nestmlParser.parse
        ("src/test/resources/org/nest/nestml/parsing/complexExpressions.nestml");

    assertTrue(root.isPresent());

    NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(Paths.get(TEST_MODEL_PATH));
    nestmlScopeCreator.runSymbolTableCreator(root.get());// do I need symbol table for the pretty printer

    final NESTMLParser parser = new NESTMLParser();
    final List<ASTExpr> expressions = AstUtils.getAll(root.get(), ASTExpr.class);
    for(final ASTExpr expr:expressions) {
      final String printedExpression = expressionsPrettyPrinter.print(expr);

      System.out.println(printedExpression);
      final Optional<ASTExpr> testant = parser.parseExpr(new StringReader(printedExpression));
      assertTrue(testant.isPresent());
    }
  }
  
}
