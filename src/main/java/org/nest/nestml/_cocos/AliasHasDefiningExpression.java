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
 * An function
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasDefiningExpression implements SPLASTDeclarationCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_DEFINING_EXPRESSION";

  @Override
  public void check(final ASTDeclaration decl) {
    if (decl.isFunction()) {
      if (!decl.getExpr().isPresent()) {
        NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
        final String msg = errorStrings.getErrorMsg(this);

        error(msg, decl.get_SourcePositionStart());
      }

    }

  }

}
