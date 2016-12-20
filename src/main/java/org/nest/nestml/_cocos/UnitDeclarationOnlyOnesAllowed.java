/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.units._ast.ASTUnitType;
import org.nest.units._cocos.UnitsASTUnitTypeCoCo;

import static de.se_rwth.commons.logging.Log.warn;

/**
 *
 *
 * @author ptraeder
 */
public class UnitDeclarationOnlyOnesAllowed implements UnitsASTUnitTypeCoCo{
  public static final String ERROR_CODE = "NESTML_UNIT_DECLARATION_ONLY_ONES_ALLOWED";

  @Override
  public void check(ASTUnitType node) {
    if(node.unitlessLiteralIsPresent()){
      int literal = node.getUnitlessLiteral().get().getValue();
      if(literal != 1){
        String errorMsg = NestmlErrorStrings.getInstance().getErrorMsg(this);
        warn(errorMsg,node.get_SourcePositionStart());
      }
    }

  }

}
