/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTNodes;

/**
 * Invariants expressions must be of the type boolea.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.2
 */
public class BooleanInvariantExpressions implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_INVARIANTS_WITH_CORRECT_VARIABLES";


  public void check(final ASTAliasDecl alias) {
    final ExpressionTypeCalculator expressionTypeCalculator = new ExpressionTypeCalculator();

    for (final ASTExpr invariantExpr:alias.getInvariants()) {
      final Either<TypeSymbol, String> expressionType = expressionTypeCalculator.computeType(invariantExpr);

      if (expressionType.isLeft()) {

        if (!expressionType.getLeft().get().equals(PredefinedTypes.getBooleanType())) {
          final String msg = "The type of the invariant expression must be boolean and not: " +
              expressionType;
          Log.error(ERROR_CODE + ":" + msg, invariantExpr.get_SourcePositionStart());
        }
      }
      else {
        Log.warn("Cannot compute the type: " + ASTNodes.toString(invariantExpr));
      }

    }

  }


}
