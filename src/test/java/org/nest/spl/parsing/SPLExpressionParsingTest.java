/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.parsing;

import de.monticore.antlr4.MCConcreteParser;
import de.se_rwth.commons.Names;
import org.antlr.v4.runtime.RecognitionException;
import org.junit.Test;
import org.nest.DisableFailQuickMixin;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._parser.ExprMCParser;
import org.nest.spl._parser.SPLParserFactory;

import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Tests, that the unary minus (-1) are recognized correctly.
 *
 * @author plotnikov
 */
public class SPLExpressionParsingTest extends DisableFailQuickMixin {

  public Optional<ASTExpr> parse(String input) throws RecognitionException, IOException {
    ExprMCParser parser = SPLParserFactory.createExprMCParser();
    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    Optional<ASTExpr> res = parser.parse(new StringReader(input));
    return res;
  }

  @Test
  public void testPlus() throws IOException {
    Optional<ASTExpr> res = parse("-a");
    assertTrue(res.isPresent());
    assertEquals("a", Names.getQualifiedName(res.get().getTerm().get().getQualifiedName().get().getParts()));
    assertTrue(res.get().isUnaryMinus());

  }


  @Test
  public void testNumber() throws IOException {
    Optional<ASTExpr> res = parse("-11");
    //System.out.println(createPrettyPrinterForTypes().prettyprint(res.get().getTerm().get()));
    assertTrue(res.get().isUnaryMinus());

  }

}
