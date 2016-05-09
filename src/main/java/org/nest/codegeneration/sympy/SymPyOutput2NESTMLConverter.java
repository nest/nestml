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
public class SymPyOutput2NESTMLConverter {

  private final NESTMLParser stringParser = new NESTMLParser();
  private final NESTMLParser fileParser = new NESTMLParser();

  public SymPyOutput2NESTMLConverter() {
    stringParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  List<ASTAliasDecl> convertToAlias(final Path declarationFile) {
    try {
      return Files.lines(declarationFile)
          .map(this::convertStringToAlias)
          .collect(Collectors.toList());
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  ASTAliasDecl convertStringToAlias(final String declarationAsString) {
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

  private ASTAliasDecl convertToAlias(final ASTDeclaration astDeclaration) {
    final ASTAliasDecl astAliasDecl = NESTMLNodeFactory.createASTAliasDecl();

    astAliasDecl.setDeclaration(astDeclaration);

    return astAliasDecl;
  }

  ASTAssignment convertToAssignment(final Path assignmentPath) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return fileParser.parseAssignment(assignmentPath.toString()).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }
  }

  ASTAssignment convertStringToAssignment(final String assignmentAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return stringParser.parseAssignment(new StringReader(assignmentAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  ASTDeclaration convertStringToDeclaration(final String declarationAsString) {
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
