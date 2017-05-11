/*
 * VarHasTypeName.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTParameter;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Checks that the variable name is not a type name, e.g. integer integer = 1.
 *
 * @author ippen, plotnikov
 */
public class FunctionParameterHasTypeName implements NESTMLASTFunctionCoCo {

  @Override
  public void check(final ASTFunction astDeclaration) {
    checkArgument(astDeclaration.getEnclosingScope().isPresent(), "Declaration hast no scope. Run symboltable creator.");
    final Scope scope = astDeclaration.getEnclosingScope().get();
    if (astDeclaration.getParameters().isPresent()) {
      final List<String> parameterNames = astDeclaration.getParameters().get().getParameters()
          .stream()
          .map(ASTParameter::getName)
          .collect(Collectors.toList());

      for (String varName : parameterNames) {
        // tries to resolve the variable name as type. if it is possible, then the variable name clashes with type name is reported as an error
        final Optional<TypeSymbol> res = scope.resolve(varName, TypeSymbol.KIND);
        // could resolve type as variable, report an error
        res.ifPresent(typeSymbol -> Log.error(
            NestmlErrorStrings.message(this, varName),
            astDeclaration.get_SourcePositionEnd()));

      }

    }

  }

}
