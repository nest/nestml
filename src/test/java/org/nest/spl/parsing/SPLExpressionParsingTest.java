package org.nest.spl.parsing;

import de.monticore.antlr4.MCConcreteParser;
import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import de.se_rwth.commons.Names;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.antlr.v4.runtime.RecognitionException;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl._parser.SPLParser;

import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class SPLExpressionParsingTest {

  @BeforeClass
  public static void disableFailQuick() {
    Log.enableFailQuick(false);
  }

  public Optional<ASTExpr> parse(String input) throws RecognitionException, IOException {
    final SPLParser parser = new SPLParser();
    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    return parser.parseExpr(new StringReader(input));
  }

  @Test
  public void testPlus() throws IOException {
    Optional<ASTExpr> res = parse("-a");
    assertTrue(res.isPresent());
    assertEquals("a", res.get().getTerm().get().getVariable().get().toString());
    assertTrue(res.get().isUnaryMinus());

  }


  @Test
  public void testNumber() throws IOException {
    final Optional<ASTExpr> res = parse("-11");
    //System.out.println(createPrettyPrinterForTypes().prettyprint(res.get().getTerm().get()));
    assertTrue(res.get().isUnaryMinus());

  }

}
