/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;

import java.util.List;

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
      final String msg = "Neurons need some outputs.";
     error(ERROR_CODE + ":" +  msg, neuron.get_SourcePositionStart());
    }

  }

}
