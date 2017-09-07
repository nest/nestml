/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.*;

import java.util.List;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Neurons must have input block.
 *
 * @author ippen, plotnikov
 */
public class NeuronWithMultipleOrNoInput implements NESTMLASTNeuronCoCo {

  public void check(final ASTNeuron neuron) {
    List<ASTInput> inputBlocks = neuron.getInputs();
    if (inputBlocks.size() == 0) {
      final String msg = NestmlErrorStrings.errorNoInput(this);
      error(msg, neuron.get_SourcePositionStart());
    }
    else if (inputBlocks.size() == 1) {
      final List<ASTInputLine> inputs = neuron.getInputLines();

      if (inputs.isEmpty()) {
        final String msg = NestmlErrorStrings.errorNoInput(this);

        error(msg, neuron.get_SourcePositionStart());
      }

    }
    else { // #inputs > 1
      final String msg = NestmlErrorStrings.errorMultipleInputs(this);
      error(msg, neuron.get_SourcePositionStart());
    }

  }

}
