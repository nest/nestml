package org.nest.nestml.cocos;


import de.monticore.cocos.CoCoLog;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;

public class NeuronNeedsDynamics implements NESTMLASTNeuronCoCo {


  public static final String ERROR_CODE = "NESTML_NEURON_NEEDS_DYNAMICS";

  public void check(ASTNeuron neuron) {
    ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(neuron.getBody());

    if (bodyDecorator.getDynamics().isEmpty()) {
      final String msg = "Neurons need at least one dynamics function.";
      CoCoLog.error(ERROR_CODE, msg, neuron.get_SourcePositionStart());
    }

    if (bodyDecorator.getDynamics().size() > 1) {
      final String msg = "Neurons need at most one dynamics function.";
      CoCoLog.error(ERROR_CODE, msg, neuron.get_SourcePositionStart());
    }

  }


}
