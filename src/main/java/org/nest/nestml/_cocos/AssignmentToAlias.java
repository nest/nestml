/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Every alias declaration has exactly one variable
 *
 * @author (last commit) ippen, plotnikov
 */
public class AssignmentToAlias implements SPLASTAssignmentCoCo {

  public static final String ERROR_CODE = "NESTML_Assignment";

  @Override
  public void check(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "Run symboltable creator.");

    final Scope scope =  astAssignment.getEnclosingScope().get();
    final String variableName = astAssignment.getLhsVarialbe().toString();
    final VariableSymbol lhsVariable = VariableSymbol.resolve(variableName, scope);
    if (lhsVariable.isAlias()) {
      String msg = NestmlErrorStrings.getInstance().getErrorMsg(this, variableName);

      error(msg, astAssignment.get_SourcePositionStart());
    }

  }

}
