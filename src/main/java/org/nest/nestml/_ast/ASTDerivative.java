/*
 * ASTDerivative.java
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

import com.google.common.base.Strings;

import java.util.List;

/**
 * HW extension of the AST class. Provides method to print the variable name.
 *
 * @author plotnikov
 */
public class ASTDerivative extends ASTDerivativeTOP {

  public ASTDerivative(
      final String name,
      final List<String> differentialOrder) {
    super(name, differentialOrder);
  }

  public ASTDerivative() {
  }

  @Override
  public String toString() {

    return name + Strings.repeat("'", getDifferentialOrder().size());
  }

  public String getSimpleName() {
    return name;
  }

  public String getNameOfDerivedVariable() {
    return name + Strings.repeat("'", Math.max(0, getDifferentialOrder().size() - 1));
  }

}
