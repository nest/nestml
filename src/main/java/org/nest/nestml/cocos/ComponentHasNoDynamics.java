package org.nest.nestml.cocos;


import de.monticore.cocos.CoCoLog;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;

public class ComponentHasNoDynamics implements NESTMLASTComponentCoCo {


  public static final String ERROR_CODE = "NESTML_COMPONENT_HAS_NO_DYNAMICS";

  public void check(ASTComponent comp) {
    if (comp.getBody() != null) {
      ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(comp.getBody());

      if (!bodyDecorator.getDynamics().isEmpty()) {
        final String msg = "Components do not have dynamics function.";
        CoCoLog.error(
            ERROR_CODE,
            msg,
            comp.get_SourcePositionStart());
      }

    }

  }


}
