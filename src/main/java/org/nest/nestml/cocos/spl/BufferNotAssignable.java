package org.nest.nestml.cocos.spl;

import com.google.common.base.Preconditions;
import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.Optional;

public class BufferNotAssignable implements SPLASTAssignmentCoCo {

  public static final String ERROR_CODE = "NESTML_SPL_BUFFER_NOT_ASSIGNABLE";

  public void check(final ASTAssignment assignment) {
    final Optional<? extends Scope> enclosingScope = assignment.getEnclosingScope();
    Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + assignment);
    final String varName = Names.getQualifiedName(assignment.getVariableName().getParts());

    Optional<NESTMLVariableSymbol> var = enclosingScope.get().resolve(varName, NESTMLVariableSymbol.KIND);

    if (!var.isPresent()) {
      Log.warn("Cannot resolve the variable: " + varName + " . Thereofore, the coco is skipped.");
    }
    else if (var.get().getBlockType() == NESTMLVariableSymbol.BlockType.BUFFER) {

      final String msg = "Buffer '" + var.get().getName() + "' cannot be reassigned.";
      CoCoLog.error(ERROR_CODE, msg, assignment.get_SourcePositionStart());
    }

  }

}
