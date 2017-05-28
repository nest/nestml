/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Every function declaration has exactly one variable
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasOneVar implements SPLASTDeclarationCoCo {

  @Override
  public void check(final ASTDeclaration decl) {
    if (decl.isFunction()) {
      if (decl.getVars().size() != 1) {
        final String msg = NestmlErrorStrings.message(this, decl.get_SourcePositionStart());

        error(msg, decl.get_SourcePositionStart());
      }

    }

  }

}
