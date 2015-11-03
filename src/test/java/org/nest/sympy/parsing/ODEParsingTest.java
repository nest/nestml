package org.nest.sympy.parsing;

import de.monticore.antlr4.MCConcreteParser;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.antlr.v4.runtime.RecognitionException;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.nestml._parser.EqMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._parser.ODEMCParser;
import org.nest.nestml._parser.OdeDeclarationMCParser;
import org.nest.spl._ast.ASTEq;
import org.nest.spl._ast.ASTODE;
import org.nest.spl._ast.ASTOdeDeclaration;

import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

public class ODEParsingTest {

  @BeforeClass
  public static void disableFailQuick() {
    Log.enableFailQuick(false);
  }

  public Optional<ASTODE> parseOde(String input) throws RecognitionException, IOException {
    ODEMCParser parser = NESTMLParserFactory.createODEMCParser();

    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    Optional<ASTODE> res = parser.parse(new StringReader(input));
    return res;
  }

  public Optional<ASTEq> parseEq(String input) throws RecognitionException, IOException {
    EqMCParser parser = NESTMLParserFactory.createEqMCParser();

    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    Optional<ASTEq> res = parser.parse(new StringReader(input));
    return res;
  }


  public Optional<ASTOdeDeclaration> parseOdeDeclaration(String input) throws RecognitionException, IOException {
    OdeDeclarationMCParser parser = NESTMLParserFactory.createOdeDeclarationMCParser();

    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    return parser.parse(new StringReader(input));
  }

  @Test
  public void testOdeDefinition() throws IOException {
    final String odeDeclarationAsString =
            "ODE:\n" +
            "  I === w * (E/tau_in) * t * exp(-1/tau_in*t)\n" +
            "  d/dt V === -1/Tau * V + 1/C*I\n" +
            "end";
    Optional<ASTOdeDeclaration> res = parseOdeDeclaration(odeDeclarationAsString);
    assertTrue(res.isPresent());
  }

  @Test
  public void testOde() throws IOException {
    Optional<ASTODE> res = parseOde("d/dt V === -1/Tau * V + 1/C*I");
    assertTrue(res.isPresent());

  }

  @Test
  public void testEq() throws IOException {
    Optional<ASTEq> res = parseEq("I === w * (E/tau_in) * t * exp(-1/tau_in*t)");
    assertTrue(res.isPresent());

  }


}
