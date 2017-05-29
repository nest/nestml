/*
 * NESTMLSymbols.java
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
package org.nest.symboltable;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.resolving.ResolvedSeveralEntriesException;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._symboltable.MethodSignaturePredicate;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static java.util.stream.Collectors.toList;

/**
 * Provides convenience methods
 *
 * @author plotnikov
 */
public class NestmlSymbols {
  public static Optional<MethodSymbol> resolveMethod(final ASTFunctionCall astFunctionCall) {
    checkArgument(astFunctionCall.getEnclosingScope().isPresent(), "Run symbol table creator");

    final List<String> callTypes = AstUtils.getParameterTypes(astFunctionCall);
    return resolveMethod(astFunctionCall.getCalleeName(), callTypes, astFunctionCall.getEnclosingScope().get());
  }

  public static Optional<MethodSymbol> resolveMethod(final ASTFunction astFunction) {
    checkArgument(astFunction.getEnclosingScope().isPresent(), "Run symbol table creator");

    final List<String> callTypes;
    if (astFunction.getParameters().isPresent()) {
      callTypes = astFunction.getParameters().get().getParameters()
          .stream()
          .map(astParameter -> AstUtils.computeTypeName(astParameter.getDatatype()))
          .collect(toList());
    }
    else {
      callTypes = Lists.newArrayList();
    }

    return resolveMethod(astFunction.getName(), callTypes, astFunction.getEnclosingScope().get());
  }

  public static Optional<MethodSymbol> resolveMethod(
      final String methodName, final List<String> parameterTypes, final Scope scope) {

    final MethodSignaturePredicate signaturePredicate = new MethodSignaturePredicate(methodName, parameterTypes);
    @SuppressWarnings("unchecked")
    final Collection<Symbol> standAloneFunction = scope.resolveMany(
        methodName, MethodSymbol.KIND, signaturePredicate)
        .stream()
        .filter(signaturePredicate) // TODO is it a bug in MC?
        .collect(toList());


    final String calleeVariableNameCandidate = Names.getQualifier(methodName);
    final String simpleMethodName = Names.getSimpleName(methodName);

    if (!calleeVariableNameCandidate.isEmpty()) {
      final Optional<VariableSymbol> calleeVariableSymbol = scope.resolve(calleeVariableNameCandidate, VariableSymbol.KIND);
      if (calleeVariableSymbol.isPresent()) {

        final Optional<MethodSymbol> builtInMethod
            = calleeVariableSymbol.get().getType().getBuiltInMethod(simpleMethodName); // TODO parameters are not considered!
        if (standAloneFunction.size() > 0 && builtInMethod.isPresent()) {
          // TODO is that possible?
          final String errorDescription = "Unambiguous function exception. Function '"
              + simpleMethodName + "'. Can be resolved as a standalone function and as a method of: '"
              + calleeVariableSymbol + "' variable.";

          throw new RuntimeException(errorDescription);
        }

        if (builtInMethod.isPresent()) {
          return builtInMethod;
        }

      }

    }

    if (standAloneFunction.size() > 0) {
      return Optional.of((MethodSymbol)standAloneFunction.iterator().next());
    }
    else {
      return Optional.empty();
    }
  }


  public static Optional<VariableSymbol> resolve(final String variableName, final Scope scope) {
    try {
      return scope.resolve(variableName, VariableSymbol.KIND);
    }
    catch (ResolvedSeveralEntriesException e) {
      Log.trace("The variable '" + variableName + "' is defined multiple times.", NestmlSymbols.class.getSimpleName());
    }
    return Optional.empty();
  }

  public static boolean isSetterPresent(
      final String aliasVar,
      final String varTypeName,
      final Scope scope) {
    final String setterName = "set_" + aliasVar;
    final Optional<MethodSymbol> setter = NestmlSymbols.resolveMethod(
        setterName, Lists.newArrayList(varTypeName), scope
    );

    if (!setter.isPresent()) {
      return false;
    }
    else {
      final TypeSymbol setterType = setter.get().getParameterTypes().get(0);

      return setterType.getName().endsWith(varTypeName);
    }

  }

  public static boolean isGetterPresent(
      final String aliasVar,
      final String varTypeName,
      final Scope scope) {
    final String setterName = "get_" + aliasVar;
    final Optional<MethodSymbol> setter = NestmlSymbols.resolveMethod(
        setterName, Lists.newArrayList(varTypeName), scope
    );

    if (!setter.isPresent()) {
      return false;
    }
    else {
      final TypeSymbol setterType = setter.get().getParameterTypes().get(0);

      return setterType.getName().endsWith(varTypeName);
    }

  }

}
