/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;

import java.util.List;

/**
 * Neurons must have input block.
 *
 * @author ippen, plotnikov
 */
public class NeuronWithoutInput implements NESTMLASTNeuronCoCo {

  public static final String ERROR_CODE = "NESTML_NEURON_WITHOUT_INPUT";

  public void check(final ASTNeuron neuron) {
    final ASTBody bodyDecorator = (neuron.getBody());

    final List<ASTInputLine> inputs = bodyDecorator.getInputLines();

    if (inputs.isEmpty()) {
      final String msg = "Neurons need some inputs.";
     error(ERROR_CODE + ":" +  msg, neuron.get_SourcePositionStart());
    }

  }

}
