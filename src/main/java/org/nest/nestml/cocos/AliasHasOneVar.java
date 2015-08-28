package org.nest.nestml.cocos;


import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;

public class AliasHasOneVar implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_ONE_VAR";

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isAlias()) {
      if (decl.getDeclaration().getVars().size() != 1) {
        final String msg = "'alias' declarations must only declare one variable.";

       error(ERROR_CODE + ":" +  msg, decl.get_SourcePositionStart());
      }

    }

  }

}
