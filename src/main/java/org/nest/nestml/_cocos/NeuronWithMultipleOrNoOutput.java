/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutputBlock;

import java.util.List;

/**
 * Prohibits multiple output blocks
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class NeuronWithMultipleOrNoOutput implements NESTMLASTNeuronCoCo {

  public void check(ASTNeuron neuron) {
    ASTNeuron bodyDecorator = (neuron);
    final List<ASTOutputBlock> outputs = bodyDecorator.getOutputBlocks();

    if (outputs.size() == 0) {
      final String msg = NestmlErrorStrings.errorNoOutput(this);
      Log.error(msg, neuron.get_SourcePositionStart());

    }
    else if (outputs.size() >  1) {
      final String msg = NestmlErrorStrings.errorMultipleOutputs(this);
      Log.error(msg, neuron.get_SourcePositionStart());

    }

  }

}
