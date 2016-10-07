/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.prettyprinter;

import org.junit.Test;
import org.nest.commons._ast.ASTExpr;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.io.StringReader;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests prettyprinter on the most available models in test resources.
 *
 * @author plotnikov
 */
public class ExpressionsPrettyPrinterTest {
  private final SPLParser splFileParser = new SPLParser();
  private final ExpressionsPrettyPrinter expressionsPrettyPrinter = new ExpressionsPrettyPrinter();
  private static final String TEST_MODEL_PATH = "src/test/resources/";

  @Test
  public void testThatPrettyPrinterProducesParsableOutput() throws IOException {

    final Optional<ASTSPLFile> root = splFileParser.parse
        ("src/test/resources/org/nest/spl/parsing/complexExpressions.simple");
    assertTrue(root.isPresent());

    SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    splScopeCreator.runSymbolTableCreator(root.get());// do I need symbol table for the pretty printer

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
