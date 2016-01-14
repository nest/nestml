/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.parsing;

import de.monticore.antlr4.MCConcreteParser;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Tests whether the model can be parsed or not
 */
public class SPLParsingTest {
  private final static  String MODELS_PARSABLE_FOLDER = "src/test/resources/org/nest/spl/parsing";
  private final static  String MODELS_COCOS_FOLDER = "src/test/resources/org/nest/spl/cocos";
  private final static  String LOG_NAME = SPLParsingTest.class.getName();
  private final SPLParser parser = new SPLParser();

  @Test
  public void testParsableModels() throws IOException {
    for (File file: new File(MODELS_PARSABLE_FOLDER).listFiles()) {
      Log.trace("Processes the following file: %s" + file.getAbsolutePath(), LOG_NAME);

      Optional<ASTSPLFile> ast = parser.parse(file.getAbsolutePath());
      assertTrue(ast.isPresent());
    }

  }

  @Test
  public void testModelsForCocos() throws IOException {
    for (File file: new File(MODELS_COCOS_FOLDER).listFiles()) {
      Log.trace("Processes the following file: %s" + file.getAbsolutePath(), LOG_NAME);

      Optional<ASTSPLFile> ast = parser.parse(file.getAbsolutePath());
      assertTrue(ast.isPresent());
    }

  }

  @Test
  public void rightAssociativeExpression() throws IOException {
    final SPLParser splParser = new SPLParser();
    splParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    final Optional<ASTExpr> result = splParser.parseExpr(new StringReader("e1**e2**e3"));

    // asserts that the parse tree is built as e1**(e2**e3), e.g. in a right associative way
    final String base = Names.getQualifiedName(result.get().getBase().get().getQualifiedName().get().getParts());
    assertEquals("e1", base);
    assertTrue(result.get().getExponent().get().isPow());
  }

}
