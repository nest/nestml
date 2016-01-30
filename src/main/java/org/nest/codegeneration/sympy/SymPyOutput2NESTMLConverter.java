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
import java.nio.file.Path;

/**
 * Takes output from the SymPy script and converts into the NESTML ASTs.
 *
 * @author plotnikov
 */
public class SymPyOutput2NESTMLConverter {

  final NESTMLParser stringParser = new NESTMLParser();
  final NESTMLParser fileParser = new NESTMLParser();

  public SymPyOutput2NESTMLConverter() {
    stringParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  public ASTAliasDecl convertToAlias(final Path declarationFile) {
    try {
      final ASTDeclaration declaration = fileParser.parseDeclaration(declarationFile.toString()).get();
      // it is ok to call get, since otherwise it is an error in the file structure
      return convertToAlias(declaration);
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  public ASTAliasDecl convertStringToAlias(final String declarationAsString) {
    try {
      final ASTDeclaration declaration = stringParser.parseDeclaration(
          new StringReader(declarationAsString)).get();
      // it is ok to call get, since otherwise it is an error in the file structure
      return convertToAlias(declaration);
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  public ASTAliasDecl convertToAlias(final ASTDeclaration astDeclaration) {
    final ASTAliasDecl astAliasDecl = NESTMLNodeFactory.createASTAliasDecl();

    astAliasDecl.setDeclaration(astDeclaration);

    return astAliasDecl;
  }

  public ASTAssignment convertToAssignment(final Path assignmentPath) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return fileParser.parseAssignment(assignmentPath.toString()).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }
  }

  public ASTAssignment convertStringToAssignment(final String assignmentAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return stringParser.parseAssignment(new StringReader(assignmentAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

}
