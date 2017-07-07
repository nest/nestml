/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.antlr4.MCConcreteParser;
import org.nest.nestml._ast.*;
import org.nest.nestml._parser.NESTMLParser;

import java.io.IOException;
import java.io.StringReader;

/**
 * Takes a string or file serialization of an NESTML model and creates a corresponding AST from it.
 *
 * @author plotnikov
 */
public class AstCreator {

  private static final NESTMLParser PARSER = new NESTMLParser();

  static {
    PARSER.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  static ASTEquation createEquation(final String equation) {
    try {

      return PARSER.parseEquation(new StringReader(equation)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse equations statement. Should not happen by construction";
      throw new RuntimeException(msg, e);
    }

  }

  static ASTAssignment createAssignment(final String assignmentAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return PARSER.parseAssignment(new StringReader(assignmentAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static ASTDeclaration createDeclaration(final String declarationAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return PARSER.parseDeclaration(new StringReader(declarationAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static ASTStmt createStatement(final String statementAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return PARSER.parseStmt(new StringReader(statementAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static public ASTVar_Block createInternalBlock() {
    final ASTVar_Block astVar_block =  NESTMLNodeFactory.createASTVar_Block();
    astVar_block.setInternals(true);

    return astVar_block;
  }
}
