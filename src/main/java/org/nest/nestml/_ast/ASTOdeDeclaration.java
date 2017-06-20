/*
 * ASTOdeDeclaration.java
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

import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTOdeDeclarationTOP;
import org.nest.nestml._ast.ASTOdeFunction;
import org.nest.nestml._ast.ASTShape;

import java.util.List;

/**
 * HW extension for the ODE block. Provides getter method to get shapes and equations.
 *
 * @author plotnikov
 */
public class ASTOdeDeclaration extends ASTOdeDeclarationTOP {
  public ASTOdeDeclaration() {

  }

  public ASTOdeDeclaration(
      final List<ASTEquation> equations,
      final List<ASTShape> shapes,
      final List<ASTOdeFunction> oDEAliass,
      final List<String> nEWLINEs) {
    super(equations, shapes, oDEAliass, nEWLINEs);
  }

  @Override
  public List<ASTShape> getShapes() {
    return shapes;
  }

  public List<ASTEquation> getODEs() {
    return equations;
  }
}
