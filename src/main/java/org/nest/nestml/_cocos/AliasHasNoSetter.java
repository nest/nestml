/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.helpers.AliasInverter;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.utils.ASTUtils;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.utils.NESTMLSymbols.isSetterPresent;

/**
 * Informs tha
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
      final String varTypeName = ASTUtils.computeTypeName(decl.getDatatype());
      if (isSetterPresent(aliasVar, varTypeName, scope) || AliasInverter.isRelativeExpression(decl.getExpr().get())) {
        Log.trace("The setter will be generated or used for the alias  at " + alias.get_SourcePositionStart().toString(), ERROR_CODE);
      }

    }

  }

}
