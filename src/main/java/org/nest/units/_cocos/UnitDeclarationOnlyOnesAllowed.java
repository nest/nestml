/*
 * UnitDeclarationOnlyOnesAllowed.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.units._cocos;

import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.units._ast.ASTUnitType;

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
        warn(errorMsg, node.get_SourcePositionStart());
      }

    }

  }

}
