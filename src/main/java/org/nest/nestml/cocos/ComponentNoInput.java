package org.nest.nestml.cocos;


import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;

import static de.se_rwth.commons.logging.Log.error;

public class ComponentNoInput implements NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_COMPONENT_NO_INPUT";

  @Override
  public void check(ASTComponent comp) {
    ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(comp.getBody());

    if (bodyDecorator.getInputLines() != null) { // TODO null check makes no sense
      if (!bodyDecorator.getInputLines().isEmpty()) {
        final String msg = "Components cannot have inputs, since they are no elements of a neuronal network.";
       error(ERROR_CODE + ":" + msg, comp.get_SourcePositionStart());
      }

    }

  }

}
