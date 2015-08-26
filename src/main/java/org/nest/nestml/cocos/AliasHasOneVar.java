package org.nest.nestml.cocos;


import de.monticore.cocos.CoCoLog;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;

public class AliasHasOneVar implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_ONE_VAR";

  @Override
  public void check(final ASTAliasDecl decl) {
    if (decl.isAlias()) {
      if (decl.getDeclaration().getVars().size() != 1) {
        final String msg = "'alias' declarations must only declare one variable.";

        CoCoLog.error(ERROR_CODE, msg, decl.get_SourcePositionStart());
      }

    }

  }

}
