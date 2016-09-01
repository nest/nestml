/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;

import java.util.List;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Neurons must have output block.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class NeuronWithoutOutput implements NESTMLASTNeuronCoCo {

  public static final String ERROR_CODE = "NESTML_NEURON_WITHOUT_OUTPUT";

  public void check(ASTNeuron neuron) {
    final ASTBody bodyDecorator = neuron.getBody();

    final List<ASTOutput> inputs = bodyDecorator.getOutputs();

    if (inputs.isEmpty()) {
      CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
      final String msg = errorStrings.getErrorMsg(this);

     error(msg, neuron.get_SourcePositionStart());
    }

  }

}
