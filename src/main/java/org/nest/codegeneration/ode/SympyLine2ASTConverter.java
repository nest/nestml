package org.nest.codegeneration.ode;

import de.monticore.antlr4.MCConcreteParser;
import org.nest.nestml._parser.DeclarationMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.spl._ast.ASTDeclaration;

import java.io.IOException;
import java.io.StringReader;

public class SympyLine2ASTConverter {
  private final DeclarationMCParser parser;

  public SympyLine2ASTConverter() {
    this.parser = NESTMLParserFactory.createDeclarationMCParser();
    this.parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  public ASTDeclaration convert(String sympyExpression) {

    try {
      return parser.parse(new StringReader(sympyExpression)).get();
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot parse the line: " + sympyExpression);
    }

  }

}
