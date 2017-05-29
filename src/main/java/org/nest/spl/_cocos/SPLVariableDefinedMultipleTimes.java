/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTBlock;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Collection;
import java.util.List;

/**
 * Checks that variables are defined only one a a scope. Of course, they can be shadowed through the embedded scope.
 * The ASTBlock block instead of ASTDeclaration is used to filter MemberDeclarations.
 * TODO: this issue reports more errors, since ASTBlock is composite structure. The coco is checked of the toplevel block
 * and all embedded block. Thus, some of variables are potentially checked multiple times.
 * @author ippen, plotnikov
 */
public class SPLVariableDefinedMultipleTimes implements SPLASTBlockCoCo {

  @Override
  public void check(final ASTBlock astBlock) {
    final List<ASTDeclaration> declarations = AstUtils.getAll(astBlock, ASTDeclaration.class);

    declarations.forEach(this::checkDeclaration);
  }

  private void checkDeclaration(final ASTDeclaration astDeclaration) {
    if (astDeclaration.getEnclosingScope().isPresent()) {
      final Scope scope = astDeclaration.getEnclosingScope().get();
      for (String var : astDeclaration.getVars()) {
        checkIfVariableDefinedMultipleTimes(var, scope, astDeclaration);
      }

    }
    else {
      Log.warn(SplErrorStrings.code(this) + ": Run the symboltable creator before.");
    }

  }

  private void checkIfVariableDefinedMultipleTimes(String var, Scope scope, ASTNode astDeclaration) {
    final Collection<Symbol> symbols = scope.resolveMany(var, VariableSymbol.KIND);
    if (symbols.size() > 1) {
      Log.error(SplErrorStrings.message(this, var), astDeclaration.get_SourcePositionStart());
    }

  }

}
