/*
 * DerivativeOrderAtLeastOne.java
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
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._cocos.NESTMLASTEquationCoCo;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.nestml._ast.ASTEquation;

/**
 * Syntactically it is possible to define an equation:
 * equations:
 *   V_m = I_syn # not V_m'
 * end
 *
 * @author plotnikov
 */
public class DerivativeOrderAtLeastOne implements NESTMLASTEquationCoCo {

  private final NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();

  @Override
  public void check(final ASTEquation astEq) {
    if (astEq.getLhs().getDifferentialOrder().size() == 0) {
      Log.error(errorStrings.getErrorMsg(this, astEq.getLhs().toString()), astEq.get_SourcePositionStart());
    }

  }


}
