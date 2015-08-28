package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;

public class ComponentNoOutput implements NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_COMPONENT_NO_OUPUT";

  @Override
  public void check(ASTComponent comp) {
    if (comp.getBody() != null) {
      ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(comp.getBody());
      if (bodyDecorator.getOutputs() != null) {
        if (!bodyDecorator.getOutputs().isEmpty()) {
          final String msg = "Components do not have outputs, only neurons have outputs.";
         error(ERROR_CODE + ":" +  msg, comp.get_SourcePositionStart());
        }

      }

    }

  }

}
