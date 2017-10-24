/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that buffers cannot be assigned a value.
 *
 * @author plotnikov
 */
public class BufferNotAssignable implements NESTMLASTAssignmentCoCo {

  public void check(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "Run symboltable creator.");
    final Scope enclosingScope = astAssignment.getEnclosingScope().get();
    final String varName = astAssignment.getLhsVarialbe().toString();

    final Optional<VariableSymbol> var = enclosingScope.resolve(varName, VariableSymbol.KIND);

    if (!var.isPresent()) {
      Log.trace("Cannot resolve the variable: " + varName + " . Thereofore, the coco is skipped.", BufferNotAssignable.class.getSimpleName());
    }
    else if (var.get().getBlockType() == VariableSymbol.BlockType.INPUT) {
      String msg = NestmlErrorStrings.message(this,var.get().getName());

      error(msg, astAssignment.get_SourcePositionStart());

    }

  }

}
