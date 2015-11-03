package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.SPLNodeFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Created by user on 20.05.15.
 */
public class Sympy2NESTMLConverter {


  private final SympyLine2ASTConverter line2ASTConverter;

  public Sympy2NESTMLConverter() {
    this.line2ASTConverter = new SympyLine2ASTConverter();
  }

  public List<ASTAliasDecl> convertMatrixFile2NESTML(final String filename) {
    final List<String> linesAsStrings = readMatrixElementsFromFile(filename);
    final List<ASTDeclaration> propagationElements
        = linesAsStrings.stream().map(line2ASTConverter::convert).collect(Collectors.toList());

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
