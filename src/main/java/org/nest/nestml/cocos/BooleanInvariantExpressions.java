/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

/**
 * Frontend for the Simple Programming Language (SPL)
 *
 * @author (last commit) plotnikov
 * @version $$Revision$$, 06.07.2015
 * @since 0.0.2
 */
public class BooleanInvariantExpressions implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_INVARIANTS_WITH_CORRECT_VARIABLES";

  private final PredefinedTypesFactory predefinedTypesFactory;

  public BooleanInvariantExpressions(PredefinedTypesFactory predefinedTypesFactory) {
    this.predefinedTypesFactory = predefinedTypesFactory;
  }

  public void check(final ASTAliasDecl alias) {
    final ExpressionTypeCalculator expressionTypeCalculator = new ExpressionTypeCalculator(
        predefinedTypesFactory);

    for (final ASTExpr invariantExpr:alias.getInvariants()) {
      final  NESTMLTypeSymbol expressionType = expressionTypeCalculator.computeType(invariantExpr);

      if (!expressionType.equals(predefinedTypesFactory.getBooleanType())) {
        final String msg = "The type of the invariant expression must be boolean and not: " +
            expressionType;
        Log.error(ERROR_CODE + ":" + msg, invariantExpr.get_SourcePositionStart());
      }

    }

  }


}
