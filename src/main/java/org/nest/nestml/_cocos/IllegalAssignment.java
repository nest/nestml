package org.nest.nestml._cocos;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

/**
 * Parameter nodes cannot be assigned to outside of the parameter block
 *
 * @author ptraeder
 */
public class IllegalAssignment implements NESTMLASTAssignmentCoCo {

  @Override
  public void check(final ASTAssignment node) {
    checkArgument(node.getEnclosingScope().isPresent(), "Run symboltable creator.");

    //resolve LHSVariable
    final Scope scope =  node.getEnclosingScope().get();
    final String variableName = node.getLhsVarialbe().toString();
    final VariableSymbol lhsVariable = VariableSymbol.resolve(variableName,scope);

    if(lhsVariable.isParameter()){
      String msg = NestmlErrorStrings.errorAssignmentToParameter(this, variableName, node.get_SourcePositionStart());
      error(msg, node.get_SourcePositionStart());
    }

    else if (lhsVariable.isInternal()) {
      String msg = NestmlErrorStrings.errorAssignmentToInternal(this, variableName, node.get_SourcePositionStart());

      error(msg, node.get_SourcePositionStart());
    }

    else if(lhsVariable.isInEquation()) {
      String msg = NestmlErrorStrings.errorAssignmentToEquation(this, variableName, node.get_SourcePositionStart());

      error(msg, node.get_SourcePositionStart());
    }

    else if (lhsVariable.isFunction()) {
      String msg = NestmlErrorStrings.errorAssignmentToAlias(this, variableName, node.get_SourcePositionStart());

      error(msg, node.get_SourcePositionStart());
    }

  }

}