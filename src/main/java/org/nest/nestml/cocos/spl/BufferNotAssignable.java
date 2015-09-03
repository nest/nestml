
/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */package org.nest.nestml.cocos.spl;

import com.google.common.base.Preconditions;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.Optional;

public class BufferNotAssignable implements SPLASTAssignmentCoCo {

  public static final String ERROR_CODE = "NESTML_SPL_BUFFER_NOT_ASSIGNABLE";

  public void check(final ASTAssignment assignment) {
    final Optional<? extends Scope> enclosingScope = assignment.getEnclosingScope();
    checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + assignment);
    final String varName = Names.getQualifiedName(assignment.getVariableName().getParts());

    final Optional<NESTMLVariableSymbol> var = enclosingScope.get()
        .resolve(varName, NESTMLVariableSymbol.KIND);

    if (!var.isPresent()) {
      Log.warn("Cannot resolve the variable: " + varName + " . Thereofore, the coco is skipped.");
    }
    else if (var.get().getBlockType() == NESTMLVariableSymbol.BlockType.BUFFER) {
      final String msg = "Buffer '" + var.get().getName() + "' cannot be reassigned.";
      error(ERROR_CODE + ":" +  msg, assignment.get_SourcePositionStart());
    }

  }

}
