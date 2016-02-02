/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;

import static de.se_rwth.commons.logging.Log.error;

/**
 * An alias
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasDefiningExpression implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_DEFINING_EXPRESSION";

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isAlias()) {
      if (!decl.getDeclaration().getExpr().isPresent()) {
        final String msg = "'alias' must be defined through an expression.";

       error(ERROR_CODE + ":" +  msg, decl.get_SourcePositionStart());
      }

    }

  }

}
