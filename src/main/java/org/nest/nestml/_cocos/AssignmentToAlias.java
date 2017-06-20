/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Every function declaration has exactly one variable
 *
 * @author (last commit) ippen, plotnikov
 */
public class AssignmentToAlias implements NESTMLASTAssignmentCoCo {

  @Override
  public void check(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "Run symboltable creator.");

    final Scope scope =  astAssignment.getEnclosingScope().get();
    final String variableName = astAssignment.getLhsVarialbe().toString();
    final VariableSymbol lhsVariable = VariableSymbol.resolve(variableName, scope);
    if (lhsVariable.isFunction()) {
      String msg = NestmlErrorStrings.message(this, variableName);

      error(msg, astAssignment.get_SourcePositionStart());
    }

  }

}
