/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTNeuron;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Neuron must have one update block.
 *
 * @author ippen, plotnikov
 */
public class NeuronWithMultipleOrNoUpdate implements NESTMLASTNeuronCoCo {

  public void check(final ASTNeuron neuron) {

    if (neuron.getUpdateBlocks().isEmpty()) {
      final String msg = NestmlErrorStrings.getErrorMsgDynamicsNotPresent(this);

     error(msg, neuron.get_SourcePositionStart());
    }

    if (neuron.getUpdateBlocks().size() > 1) {
      final String msg = NestmlErrorStrings.getErrorMsgMultipleDynamics(this);
     error( msg, neuron.get_SourcePositionStart());
    }

  }


}
