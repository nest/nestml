/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;

import java.util.List;

/**
 * Prohibits multiple output blocks
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class MultipleOutputs implements NESTMLASTNeuronCoCo {

  public static final String ERROR_CODE = "NESTML_MULTIPLE_OUTPUTS";

  public void check(ASTNeuron neuron) {
    ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(neuron.getBody());
    final List<ASTOutput> outputs = bodyDecorator.getOutputs();

    if (outputs.size() > 1) {
      final String msg = "Neurons have at most one output and not " + outputs.size() + ".";
      Log.error(ERROR_CODE + ":" + msg, neuron.get_SourcePositionStart());
    }

  }

}
