/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.antlr4.MCConcreteParser;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Takes output from the SymPy script and converts into the NESTML ASTs.
 *
 * @author plotnikov
 */
public class NESTMLASTCreator {

  private static final NESTMLParser stringParser = new NESTMLParser();
  private static final NESTMLParser fileParser = new NESTMLParser();

  public NESTMLASTCreator() {
    stringParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  static List<ASTAliasDecl> convertToAliases(final Path declarationFile) {
    try {
      return Files.lines(declarationFile)
          .map(NESTMLASTCreator::convertStringToAlias)
          .collect(Collectors.toList());
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static ASTAliasDecl convertStringToAlias(final String declarationAsString) {
    try {
      final ASTDeclaration declaration = stringParser.parseDeclaration(
          new StringReader(declarationAsString)).get();
      // it is ok to call get, since otherwise it is an error in the file structure
      return convertToAliases(declaration);
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static private ASTAliasDecl convertToAliases(final ASTDeclaration astDeclaration) {
    final ASTAliasDecl astAliasDecl = NESTMLNodeFactory.createASTAliasDecl();

    astAliasDecl.setDeclaration(astDeclaration);

    return astAliasDecl;
  }

  static ASTAssignment convertToAssignment(final Path assignmentPath) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return fileParser.parseAssignment(assignmentPath.toString()).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }
  }

  static ASTAssignment convertStringToAssignment(final String assignmentAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return stringParser.parseAssignment(new StringReader(assignmentAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static ASTDeclaration convertStringToDeclaration(final String declarationAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return stringParser.parseDeclaration(new StringReader(declarationAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

}
