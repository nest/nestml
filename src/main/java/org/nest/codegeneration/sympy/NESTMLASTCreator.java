/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.antlr4.MCConcreteParser;
import org.nest.nestml._ast.ASTVar_Block;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._ast.ASTEquation;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Takes a string or file serialization of an NESTML model and creates a corresponding AST from it.
 *
 * @author plotnikov
 */
public class NESTMLASTCreator {

  private static final NESTMLParser PARSER = new NESTMLParser();

  static {
    PARSER.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  static List<ASTDeclaration> createDeclarations(final Path declarationFile) {
    checkArgument(Files.exists(declarationFile), declarationFile.toString());

    try {
      return Files.lines(declarationFile)
          .map(NESTMLASTCreator::createDeclaration)
          .collect(Collectors.toList());
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  static ASTEquation createEquation(final String equation) {
    try {
      final ASTEquation astEquation = PARSER.parseEquation(new StringReader(equation)).get();

      return astEquation;
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
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

  static public ASTVar_Block createInternalBlock() {
    final ASTVar_Block astVar_block =  NESTMLNodeFactory.createASTVar_Block();
    astVar_block.setInternals(true);

    return astVar_block;
  }
}
