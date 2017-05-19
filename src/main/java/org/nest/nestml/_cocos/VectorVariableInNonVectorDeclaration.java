/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTVariable;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;

import static com.google.common.base.Preconditions.checkState;
import static de.monticore.utils.ASTNodes.getSuccessors;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that an function is not used in the declaring expression of an non function declaration
 * n  integer
 * function three integer[n] = 3
 * threePlusFour integer = three + 4 <- error: threePlusFour is not a vector
 * @author plotnikov, ippen
 */
public class VectorVariableInNonVectorDeclaration implements SPLASTDeclarationCoCo {

  @Override
  public void check(final ASTDeclaration astDeclaration) {
    checkState(astDeclaration.getEnclosingScope().isPresent(), "Run symbol table creator");
    final Scope scope = astDeclaration.getEnclosingScope().get();

    if (astDeclaration.getExpr().isPresent()) {
      final List<ASTVariable> variables = getSuccessors(astDeclaration.getExpr().get(), ASTVariable.class);

      for (final ASTVariable variable : variables) {
        final VariableSymbol stentry = VariableSymbol.resolve(variable.toString(), scope);

        // used is set here
        if (stentry.isVector() && !astDeclaration.getSizeParameter().isPresent()) {
          final String msg = NestmlErrorStrings.message(this, stentry.getName(), astDeclaration.get_SourcePositionStart());
          error(msg, astDeclaration.get_SourcePositionStart());
        }

      }

    }

  }

}
