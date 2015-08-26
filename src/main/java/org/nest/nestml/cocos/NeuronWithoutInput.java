package org.nest.nestml.cocos;


import de.monticore.cocos.CoCoLog;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;

import java.util.List;

public class NeuronWithoutInput implements NESTMLASTNeuronCoCo {

  public static final String ERROR_CODE = "NESTML_NEURON_WITHOUT_INPUT";

  public void check(ASTNeuron neuron) {
    ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(neuron.getBody());

    List<ASTInputLine> inputs = bodyDecorator.getInputLines();

    if (inputs.isEmpty()) {
      final String msg = "Neurons need some inputs.";
      CoCoLog.error(ERROR_CODE, msg, neuron.get_SourcePositionStart());
    }

  }

}
