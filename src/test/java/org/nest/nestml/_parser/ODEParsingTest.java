/*
 * ODEParsingTest.java
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

package org.nest.nestml._parser;

import de.monticore.antlr4.MCConcreteParser;
import org.antlr.v4.runtime.RecognitionException;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTOdeDeclaration;

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

  private final NESTMLParser parser = new NESTMLParser();

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
