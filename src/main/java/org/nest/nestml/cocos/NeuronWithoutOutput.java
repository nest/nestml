package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;

import java.util.List;

public class NeuronWithoutOutput implements NESTMLASTNeuronCoCo {

  public static final String ERROR_CODE = "NESTML_NEURON_WITHOUT_OUTPUT";

  public void check(ASTNeuron neuron) {
    final ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(neuron.getBody());

    final List<ASTOutput> inputs = bodyDecorator.getOutputs();

    if (inputs.isEmpty()) {
      final String msg = "Neurons need some outputs.";
     error(ERROR_CODE + ":" +  msg, neuron.get_SourcePositionStart());
    }

  }

}
