/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.sympy;

import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.nestml._parser.DeclarationMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.SPLNodeFactory;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Reads entries from the python output stored in the file and creates corresponding NESTML ASTs.
 *
 * @author plotnikov
 */
public class SymPyOutput2NESTMLConverter {
  final DeclarationMCParser declarationParser = NESTMLParserFactory.createDeclarationMCParser();

  public List<ASTAliasDecl> createDeclarationASTs(final String filename) {
    final List<String> linesAsStrings = readMatrixElementsFromFile(filename);
    final List<ASTDeclaration> propagationElements
        = linesAsStrings.stream().map(this::convert).collect(Collectors.toList());

    return propagationElements.stream().map(this::convertToAlias).collect(Collectors.toList());
  }

  private ASTAliasDecl convertToAlias(ASTDeclaration astDeclaration) {
    final ASTAliasDecl astAliasDecl = NESTMLNodeFactory.createASTAliasDecl();

    astAliasDecl.setDeclaration(astDeclaration);
    astAliasDecl.setAlias(false);
    astAliasDecl.setHide(false);
    astAliasDecl.setInvariants(SPLNodeFactory.createASTExprList());

    return astAliasDecl;
  }

  public ASTDeclaration convert(String sympyExpression) {

    try {

      return declarationParser.parse(new StringReader(sympyExpression)).get();
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot parse the line: " + sympyExpression);
    }

  }

  public List<String> readMatrixElementsFromFile(final String filename) {
    List<String> matrixElements;
    try {
      matrixElements = Files.lines(new File(filename).toPath())
          .filter(line -> !line.isEmpty())
          .collect(Collectors.toList());
      return matrixElements;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot find or read the file with propagator matrix.", e);
    }

  }

}
