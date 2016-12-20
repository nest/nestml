package org.nest.spl.parsing;

import de.monticore.antlr4.MCConcreteParser;
import org.antlr.v4.runtime.RecognitionException;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.ode._parser.ODEParser;

import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests the handling of the parser for the ODE block.
 *
 * @author plornikov
 */
public class ODEParsingTest extends ModelbasedTest {

  private final ODEParser parser = new ODEParser();

  @Test
  public void testOdeDefinition() throws IOException {
    final String odeDeclarationAsString =
            "I = w * (E/tau_in) * t * exp(-1/tau_in*t)\n" +
            "V' = -1/Tau * V + 1/C*I\n" ;
    Optional<ASTOdeDeclaration> res = parseOdeDeclaration(odeDeclarationAsString);
    assertTrue(res.isPresent());
  }

  @Test
  public void testOde() throws IOException {
    Optional<ASTEquation> res = parseEquation("V' = -1/Tau * V + 1/C*I");
    assertTrue(res.isPresent());

  }

  @Test
  public void testEq() throws IOException {
    Optional<ASTEquation> res = parseEquation("I = w * (E/tau_in) * t * exp(-1/tau_in*t)");
    assertTrue(res.isPresent());

  }

  private Optional<ASTEquation> parseEquation(String input) throws RecognitionException, IOException {

    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    return parser.parseEquation(new StringReader(input));
  }


  private Optional<ASTOdeDeclaration> parseOdeDeclaration(String input) throws RecognitionException, IOException {

    return parser.parseOdeDeclaration(new StringReader(input));
  }


}
