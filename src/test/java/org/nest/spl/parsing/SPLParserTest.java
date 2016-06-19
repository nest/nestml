/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.parsing;

import de.monticore.antlr4.MCConcreteParser;
import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.*;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.utils.FilesHelper.collectSPLModelFilenames;

/**
 * Tests whether the model can be parsed or not
 */
public class SPLParserTest extends ModelbasedTest {
  private final static  String LOG_NAME = SPLParserTest.class.getName();
  private final SPLParser parser = new SPLParser();

  @Test
  public void testParsableModels() throws IOException {
    final List<Path> filenames = collectSPLModelFilenames(TEST_MODEL_PATH);

    filenames.forEach(this::parseAndCheck);
  }

  @Test
  public void rightAssociativeExpression() throws IOException {
    final SPLParser splParser = new SPLParser();
    splParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    final Optional<ASTExpr> result = splParser.parseExpr(new StringReader("e1**e2**e3"));

    // asserts that the parse tree is built as e1**(e2**e3), e.g. in a right associative way
    final String base = result.get().getBase().get().getVariable().get().toString();
    assertEquals("e1", base);
    assertTrue(result.get().getExponent().get().isPow());
  }

  private void parseAndCheck(Path file) {
    Log.info(String.format("Processes the following file: %s", file.toString()), LOG_NAME);

    Optional<ASTSPLFile> ast;
    try {
      ast = parser.parse(file.toString());
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
    assertTrue(ast.isPresent());
  }

}
