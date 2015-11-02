package org.nest.ode;

import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.SPLNodeFactory;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Created by user on 20.05.15.
 */
public class Sympy2NESTMLConverter {

  private final SympyOutputReader sympyOutputReader;

  private final SympyLine2ASTConverter line2ASTConverter;

  public Sympy2NESTMLConverter() {
    this.sympyOutputReader = new SympyOutputReader();
    this.line2ASTConverter = new SympyLine2ASTConverter();
  }

  public List<ASTAliasDecl> convertMatrixFile2NESTML(final String filename) {
    final List<String> linesAsStrings = sympyOutputReader.readMatrixElementsFromFile(filename);
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

}
