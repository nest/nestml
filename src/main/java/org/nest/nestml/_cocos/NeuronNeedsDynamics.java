/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;

/**
 * Neuron must have dynamics.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class NeuronNeedsDynamics implements NESTMLASTNeuronCoCo {


  public static final String ERROR_CODE = "NESTML_NEURON_NEEDS_DYNAMICS";

  public void check(final ASTNeuron neuron) {
    final ASTBody bodyDecorator = neuron.getBody();

    if (bodyDecorator.getDynamics().isEmpty()) {
      final String msg = "Neurons need at least one dynamics function.";
     error(ERROR_CODE + ":" +  msg, neuron.get_SourcePositionStart());
    }

    if (bodyDecorator.getDynamics().size() > 1) {
      final String msg = "Neurons need at most one dynamics function.";
     error(ERROR_CODE + ":" +  msg, neuron.get_SourcePositionStart());
    }

  }


}
