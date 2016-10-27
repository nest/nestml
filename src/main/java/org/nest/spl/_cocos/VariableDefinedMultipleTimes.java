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

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Checks that variables are defined only one a a scope. Of course, they can be shadowed through the embedded scope.
 *
 * @author ippen, plotnikov
 */
public class VariableDefinedMultipleTimes implements SPLASTBlockCoCo {

  @Override
  public void check(final ASTBlock astBlock) {
    final List<ASTDeclaration> declarations = astBlock.getStmts()
        .stream()
        .filter(astStmt -> astStmt.getSmall_Stmt().isPresent())
        .map(astStmt -> astStmt.getSmall_Stmt().get())
        .filter(astSmall_stmt -> astSmall_stmt.getDeclaration().isPresent())
        .map(astSmall_stmt -> astSmall_stmt.getDeclaration().get())
        .collect(Collectors.toList());

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
      Log.warn(SplCocoStrings.code(this) + ": Run the symboltable creator before.");
    }

  }

  private void checkIfVariableDefinedMultipleTimes(String var, Scope scope, ASTNode astDeclaration) {
    final Collection<Symbol> symbols = scope.resolveMany(var, VariableSymbol.KIND);
    if (symbols.size() > 1) {
      Log.error(SplCocoStrings.message(this, var, astDeclaration.get_SourcePositionStart()));
    }

  }

}
