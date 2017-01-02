/*
 * BlockDefinedMultipleTimes.java
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
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTVar_Block;

import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Collectors;


/**
 * Every NESTML block should be defined at most once
 *
 */
public class VariableBlockDefinedMultipleTimes implements NESTMLASTNeuronCoCo {

  public void check(final ASTNeuron neuron) {
    final ASTBody bodyDecorator = neuron.getBody();
    checkBlock(bodyDecorator, "state", ASTVar_Block::isState);
    checkBlock(bodyDecorator, "parameters", ASTVar_Block::isParameters);
    checkBlock(bodyDecorator, "internals", ASTVar_Block::isInternals);
  }

  private void checkBlock(final ASTBody astBody, final String blockName, final Predicate<ASTVar_Block> blockType) {
    final List<ASTVar_Block> blocks = filterVarBlockByType(astBody, ASTVar_Block::isState);
    if (blocks.size() > 1) {
      final String msg = NestmlErrorStrings.error(this, blocks.get(0).get_SourcePositionStart(), blockName);
      Log.error(msg);
    }

  }

  private List<ASTVar_Block> filterVarBlockByType(final ASTBody astBody, final Predicate<ASTVar_Block> blockType) {
    return astBody.getBodyElements()
        .stream()
        .filter(astBodyElement -> astBodyElement instanceof ASTVar_Block)
        .map(astBodyElement -> (ASTVar_Block) astBodyElement)
        .filter(blockType)
        .collect(Collectors.toList());
  }

}
