/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTAliasDecl;

/**
 * Every alias declaration has exactly one variable
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasOneVar implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_ONE_VAR";

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isAlias()) {
      if (decl.getDeclaration().getVars().size() != 1) {
        CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
        final String msg = errorStrings.getErrorMsg(this);

       error(msg, decl.get_SourcePositionStart());
      }

    }

  }

}
