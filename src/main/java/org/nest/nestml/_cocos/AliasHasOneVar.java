/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTAliasDecl;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Every alias declaration has exactly one variable
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasOneVar implements NESTMLASTAliasDeclCoCo {

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isAlias()) {
      if (decl.getDeclaration().getVars().size() != 1) {
        final String msg = NestmlErrorStrings.message(this, decl.get_SourcePositionStart());

        error(msg, decl.get_SourcePositionStart());
      }

    }

  }

}
