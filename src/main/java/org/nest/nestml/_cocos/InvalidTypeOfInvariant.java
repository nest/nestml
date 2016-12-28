/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

/**
 * Invariants expressions must be of the type boolea.
 *
 * @author ppen, plotnikov
 */
class InvalidTypeOfInvariant implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_INVALID_TYPE_OF_INVARIANT";
  NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();


  public void check(final ASTAliasDecl alias) {
    if (alias.getInvariant().isPresent()) {
      final Either<TypeSymbol, String> expressionType = alias.getInvariant().get().getType();

      if (expressionType.isValue()) {

        if (!expressionType.getValue().equals(PredefinedTypes.getBooleanType())) {
          final String msg = errorStrings.getErrorMsgInvariantMustBeBoolean(this,expressionType.toString());

          Log.error(msg, alias.getInvariant().get().get_SourcePositionStart());
        }
      }
      else {
        final String msg = errorStrings.getErrorMsgCannotComputeType(this,
                AstUtils.toString(alias.getInvariant().get()));

        Log.warn(msg,alias.getInvariant().get().get_SourcePositionStart());
      }

    }

  }


}
