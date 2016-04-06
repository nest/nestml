/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.utils.ASTNodes;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.utils.NESTMLSymbols.isSetterPresent;

/**
 * Every alias variable must be backed by a corresponding setter
 *
 * @author ippen, plotnikov
 */
public class AliasHasNoSetter implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_NO_SETTER";

  @Override
  public void check(final ASTAliasDecl alias) {
    final ASTDeclaration decl = alias.getDeclaration();
    checkState(decl.getEnclosingScope().isPresent(), "No scope assigned to the node: " + decl);
    final  Scope scope = decl.getEnclosingScope().get();

    if (alias.isAlias()) {
      // per default aliases have only a single variable. it is checked by the AliasHasOneVar coco.
      final String aliasVar = decl.getVars().get(0);
      final String varTypeName = ASTNodes.computeTypeName(decl.getDatatype());
      if (!isSetterPresent(aliasVar, varTypeName, scope)) {

        final String msg = "Alias-variable '" + aliasVar + "' needs a setter-function: set_"
            + aliasVar + "(v " + varTypeName + ")";
        warn(ERROR_CODE + ":" + msg, alias.get_SourcePositionStart());
      }

    }

  }

}
