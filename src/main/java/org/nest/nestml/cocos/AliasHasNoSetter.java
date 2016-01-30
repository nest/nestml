/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTNodes;
import org.nest.utils.NESTMLSymbols;

import java.util.Optional;

import static com.google.common.collect.Lists.newArrayList;
import static de.se_rwth.commons.logging.Log.error;
import static org.nest.utils.NESTMLSymbols.isSetterPresent;

/**
 * Every alias variable must be backed by a corresponding setter
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasNoSetter implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_NO_SETTER";

  @Override
  public void check(ASTAliasDecl alias) {
    final ASTDeclaration decl = alias.getDeclaration();
    Preconditions.checkState(decl.getEnclosingScope().isPresent(), "No scope assigned to the node: " + decl);
    final  Scope scope = decl.getEnclosingScope().get();

    if (alias.isAlias()) {
      // per default aliases have only a single variable. it is checked by the AliasHasOneVar coco.
      String aliasVar = decl.getVars().get(0);
      String varTypeName = ASTNodes.toString(decl.getType().get());
      if (!isSetterPresent(aliasVar, varTypeName, scope)) {
        final String msg = "Alias-variable '" + aliasVar
            + "' needs a setter-function: set_" + aliasVar
            + "(v " + decl.getType().get().toString() + ")";
        error(ERROR_CODE + ":" + msg, alias.get_SourcePositionStart());
      }

    }

  }

}
