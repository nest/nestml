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
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._parser.ExprMCParser;
import org.nest.spl._parser.SPLParserFactory;

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

  private TypesPrettyPrinterConcreteVisitor createPrettyPrinterForTypes() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }
}
