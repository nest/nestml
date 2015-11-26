/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.antlr4.MCConcreteParser;
import de.monticore.types.types._ast.TypesNodeFactory;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.nestml._parser.AssignmentMCParser;
import org.nest.nestml._parser.DeclarationMCParser;
import org.nest.nestml._parser.ExprMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._ast.SPLNodeFactory;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

import static org.nest.nestml._parser.NESTMLParserFactory.createAssignmentMCParser;
import static org.nest.nestml._parser.NESTMLParserFactory.createDeclarationMCParser;

/**
 * Takes output from the SymPy script and converts into the NESTML ASTs.
 *
 * @author plotnikov
 */
public class SymPyOutput2NESTMLConverter {

  final DeclarationMCParser declarationParser = createDeclarationMCParser();
  final DeclarationMCParser declarationStringParser = createDeclarationMCParser();
  final AssignmentMCParser assignmentStringParser = createAssignmentMCParser();

  public SymPyOutput2NESTMLConverter() {
    declarationStringParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    assignmentStringParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
  }

  public ASTAliasDecl convertToAlias(final Path declarationFile) {
    try {
      final ASTDeclaration declaration = declarationParser.parse(declarationFile.toString()).get();
      // it is ok to call get, since otherwise it is an error in the file structure
      return convertToAlias(declaration);
    }
    catch (IOException e) {
      final String msg = "Cannot parse declaration statement.";
      throw new RuntimeException(msg, e);
    }

  }

  public ASTAliasDecl convertStringToAlias(String declarationAsString) {
    try {
      final ASTDeclaration declaration = declarationStringParser
          .parse(new StringReader(declarationAsString)).get();
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
    astAliasDecl.setAlias(false);
    astAliasDecl.setHide(false);
    astAliasDecl.setInvariants(SPLNodeFactory.createASTExprList());

    return astAliasDecl;
  }

  public ASTAssignment convertToAssignment(final Path assignmentPath) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return assignmentStringParser.parse(assignmentPath.toString()).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }
  }

  public ASTAssignment convertStringToAssignment(final String assignmentAsString) {
    try {
      // it is ok to call get, since otherwise it is an error in the file structure
      return assignmentStringParser.parse(new StringReader(assignmentAsString)).get();
    }
    catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

}
