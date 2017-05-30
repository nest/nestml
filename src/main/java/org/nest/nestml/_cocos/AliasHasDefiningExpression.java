/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTDeclaration;

import static de.se_rwth.commons.logging.Log.error;

/**
 * An function
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasDefiningExpression implements NESTMLASTDeclarationCoCo {

  @Override
  public void check(final ASTDeclaration decl) {
    if (decl.isFunction()) {
      if (!decl.getExpr().isPresent()) {
        final String msg = NestmlErrorStrings.getErrorMsg(this);

        error(msg, decl.get_SourcePositionStart());
      }

    }

  }

}
