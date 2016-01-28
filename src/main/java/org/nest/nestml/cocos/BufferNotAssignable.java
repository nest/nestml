/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.INPUT_BUFFER_CURRENT;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.INPUT_BUFFER_SPIKE;

/**
 * Checks that buffers cannot be assigned a value.
 *
 * @author plotnikov
 */
public class BufferNotAssignable implements SPLASTAssignmentCoCo {

  public static final String ERROR_CODE = "NESTML_SPL_BUFFER_NOT_ASSIGNABLE";

  public void check(final ASTAssignment assignment) {
    final Optional<? extends Scope> enclosingScope = assignment.getEnclosingScope();
    checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + assignment);
    final String varName = Names.getQualifiedName(assignment.getVariableName().getParts());

    final Optional<VariableSymbol> var = enclosingScope.get()
        .resolve(varName, VariableSymbol.KIND);

    if (!var.isPresent()) {
      Log.warn("Cannot resolve the variable: " + varName + " . Thereofore, the coco is skipped.");
    }
    else if (var.get().getBlockType() == INPUT_BUFFER_CURRENT ||
        var.get().getBlockType() == INPUT_BUFFER_SPIKE) {
      final String msg = "Buffer '" + var.get().getName() + "' cannot be reassigned.";
      error(ERROR_CODE + ":" +  msg, assignment.get_SourcePositionStart());

    }

  }

}
