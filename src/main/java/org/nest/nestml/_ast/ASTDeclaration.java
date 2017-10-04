/*
 * ASTDeclaration.java
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

import com.google.common.collect.Lists;

import java.util.List;

/**
 * HWC class that stores the corresponding comment from the source model.
 *
 * @author plotnikov
 */
public class ASTDeclaration extends ASTDeclarationTOP {
  private final StringBuilder docStrings = new StringBuilder();

  protected ASTDeclaration(){

  }

  public ASTDeclaration(List<ASTVariable> vars,
                        ASTDatatype datatype,
                        String sizeParameter,
                        ASTExpr expr,
                        ASTExpr invariant,
                        boolean recordable,
                        boolean function) {
    super(vars, datatype, sizeParameter, expr, invariant, recordable, function);

  }

  public void extendDocString(final String docString) {
    docStrings.append(" ").append(docString.trim());
  }

  public String getDocString() {
    return docStrings.toString();
  }

}
