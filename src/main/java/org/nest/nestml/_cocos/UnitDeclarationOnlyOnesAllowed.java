/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._cocos.CommonsASTExprCoCo;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._ast.ASTFunction;
import org.nest.spl._ast.*;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units._ast.ASTUnitType;
import org.nest.units._cocos.UnitsASTUnitTypeCoCo;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;
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
