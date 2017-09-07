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
import org.nest.nestml._ast.ASTBlockWithVariables;
import org.nest.nestml._ast.ASTNeuron;

import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Collectors;


/**
 * Every NESTML block should be defined at most once
 *
 */
public class VariableBlockDefinedMultipleTimes implements NESTMLASTNeuronCoCo {

  public void check(final ASTNeuron neuron) {
    checkBlock(neuron, "state", ASTBlockWithVariables::isState);
    checkBlock(neuron, "parameters", ASTBlockWithVariables::isParameters);
    checkBlock(neuron, "internals", ASTBlockWithVariables::isInternals);
  }

  private void checkBlock(final ASTNeuron astNeuron, final String blockName, final Predicate<ASTBlockWithVariables> blockType) {
    final List<ASTBlockWithVariables> blocks = filterVarBlockByType(astNeuron, blockType);
    if (blocks.size() > 1) {
      final String msg = NestmlErrorStrings.error(this, blocks.get(0).get_SourcePositionStart(), blockName);
      Log.error(msg);
    }

  }

  private List<ASTBlockWithVariables> filterVarBlockByType(final ASTNeuron astNeuron, final Predicate<ASTBlockWithVariables> blockType) {
    return astNeuron.getBlockWithVariabless()
        .stream()
        .filter(blockType)
        .collect(Collectors.toList());
  }

}
