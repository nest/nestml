/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.NESTMLSymbols;

import java.util.Optional;

import static com.google.common.collect.Lists.newArrayList;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Every alias variable must be backed by a corresponding setter
 *
 * @author (last commit) ippen, plotnikov
 */
public class AliasHasNoSetter implements NESTMLASTAliasDeclCoCo {


  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_NO_SETTER";

  @Override
  public void check(ASTAliasDecl alias) {
    if (alias.isAlias()) {
      final ASTDeclaration decl = alias.getDeclaration();
      final Optional<? extends Scope> scope = decl.getEnclosingScope();
      Preconditions.checkState(scope.isPresent(), "No scope is assigned to the node: " + decl);

      // per default aliases have only a single variable. it is checked by the AliasHasOneVar coco.
      String aliasVar = decl.getVars().get(0);
      String varTypeName = Names.getQualifiedName(decl.getType().get().getParts());


      Preconditions.checkState(scope.isPresent(), "No scope assigned to the node: " + decl);
      final String setterName = "set_" + aliasVar;

      final Optional<MethodSymbol> setter = NESTMLSymbols.resolveMethod(
          scope.get(),
          setterName,
          newArrayList(varTypeName));

      if (!setter.isPresent()) {
        final String msg = "Alias-variable '" + aliasVar + "' needs a setter-function: set_" +
            aliasVar + "(v " + decl.getType().get().toString() + ")";

        error(ERROR_CODE + ":" + msg, alias.get_SourcePositionStart());
      }
      else {

        TypeSymbol setterType = setter.get().getParameterTypes().get(0);

        if (!setterType.getName().endsWith(decl.getType().get().toString())) {
          final String msg = "Alias-variable '" + aliasVar
                  + "' needs a setter-function: set_" + aliasVar
                  + "(v " + decl.getType().get().toString() + ")";

          error(ERROR_CODE + ":" + msg, alias.get_SourcePositionStart());
        }

      }


    }

  }

}
