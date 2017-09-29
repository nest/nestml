/*
 * ASTVariable.java
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

import com.google.common.base.Joiner;
import com.google.common.base.Strings;
import de.monticore.types.types._ast.ASTQualifiedName;

import java.util.List;

/**
 * HW extension of the AST class. Provides method to print the variable name.
 *
 * @author plotnikov
 */
public class ASTVariable extends ASTVariableTOP {

  public ASTVariable(
      final String name,
      final List<String> differentialOrder) {
    super(name, differentialOrder);
  }

  public ASTVariable() {
  }

  @Override
  public String toString() {
    return name + Strings.repeat("'", differentialOrder.size());
  }

}
