/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTAliasDecl;

import static de.se_rwth.commons.logging.Log.error;

/**
 * An function
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasDefiningExpression implements NESTMLASTAliasDeclCoCo {

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isFunction()) {
      if (!decl.getDeclaration().getExpr().isPresent()) {
        NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
        final String msg = errorStrings.getErrorMsg(this);

        error(msg, decl.get_SourcePositionStart());
      }

    }

  }

}
