/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Checks that the variable name is not a type name, e.g. integer integer = 1.
 *
 * @author ippen, plotnikov
 */
public class VariableHasTypeName implements SPLASTDeclarationCoCo {

  @Override
  public void check(final ASTDeclaration astDeclaration) {
    checkArgument(astDeclaration.getEnclosingScope().isPresent(), "Declaration hast no scope. Run symboltable creator.");
    final Scope scope = astDeclaration.getEnclosingScope().get();

    for (String var : astDeclaration.getVars()) {
      // tries to resolve the variable name as type. if it is possible, then the variable name clashes with type name is reported as an error
      final Optional<TypeSymbol> res = scope.resolve(var, TypeSymbol.KIND);
      // could resolve type as variable, report an error
      res.ifPresent(typeSymbol -> Log.error(
          SplErrorStrings.message(this, var), astDeclaration.get_SourcePositionEnd()));

    }

  }

}
