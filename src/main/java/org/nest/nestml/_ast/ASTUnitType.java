/*
 * ASTUnitType.java
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

package org.nest.nestml._ast;

import de.monticore.literals.literals._ast.ASTIntLiteral;

/**
 * @author ptraeder
 */
public class ASTUnitType extends ASTUnitTypeTOP{
  private String serializedUnit;

  public ASTUnitType(ASTUnitType unitType,
      ASTUnitType base,
      de.monticore.literals.literals._ast.ASTIntLiteral exponent,
      ASTUnitType left,
      ASTIntLiteral unitlessLiteral,
      ASTUnitType right,
      String unit,
      String leftParentheses,
      String rightParentheses,
      boolean divOp,
      boolean timesOp,
      boolean pow ){
    super(unitType,base,exponent,left,unitlessLiteral,right,unit,leftParentheses,rightParentheses,divOp,timesOp,pow);
  }

  public ASTUnitType() {
  }

  public String getSerializedUnit() {
    return serializedUnit;
  }

  public void setSerializedUnit(String serializedUnit) {
    this.serializedUnit = serializedUnit;
  }
}
