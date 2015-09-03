/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;

/**
 * Every alias declaration has exactly one variable
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class AliasHasOneVar implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_ONE_VAR";

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isAlias()) {
      if (decl.getDeclaration().getVars().size() != 1) {
        final String msg = "'alias' declarations must only declare one variable.";

       error(ERROR_CODE + ":" +  msg, decl.get_SourcePositionStart());
      }

    }

  }

}
