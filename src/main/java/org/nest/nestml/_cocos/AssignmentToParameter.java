package org.nest.nestml._cocos;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;


import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

/**
 * Parameter nodes cannot be assigned to outside of the parameter block
 *
 * @author ptraeder
 */
public class AssignmentToParameter implements NESTMLASTAssignmentCoCo {
  @Override
  public void check(final ASTAssignment node) {
    checkArgument(node.getEnclosingScope().isPresent(), "Run symboltable creator.");

    //resolve LHSVariable
    String lhsName = node.getLhsVarialbe().toString();
    VariableSymbol lhsVariable = VariableSymbol.resolve(lhsName,node.getEnclosingScope().get());

    if(lhsVariable.isParameter()){
      String msg = NestmlErrorStrings.errorAssignmentToParameter(this, lhsName, node.get_SourcePositionStart());
      error(msg, node.get_SourcePositionStart());
    }
  }



}