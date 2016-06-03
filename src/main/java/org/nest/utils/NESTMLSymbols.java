/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.resolving.ResolvedSeveralEntriesException;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._symboltable.MethodSignaturePredicate;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Provides convenience methods
 *
 * @author plotnikov
 */
public class NESTMLSymbols {
  public static Optional<MethodSymbol> resolveMethod(final ASTFunctionCall astFunctionCall) {
    checkArgument(astFunctionCall.getEnclosingScope().isPresent(), "Run symbol table creator");

    final List<String> callTypes = ASTUtils.getParameterTypes(astFunctionCall);
    return resolveMethod(astFunctionCall.getCalleeName(), callTypes, astFunctionCall.getEnclosingScope().get());
  }
  public static Optional<MethodSymbol> resolveMethod(
      final String methodName, final List<String> parameterTypes, final Scope scope) {

    final MethodSignaturePredicate signaturePredicate = new MethodSignaturePredicate(methodName,
        parameterTypes);
    @SuppressWarnings("unchecked")
    final Collection<Symbol> standAloneFunction = scope.resolveMany(
        methodName, MethodSymbol.KIND, signaturePredicate)
        .stream()
        .filter(signaturePredicate) // TODO is it a bug in MC?
        .collect(Collectors.toList());


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
      Log.warn("The variable '" + variableName + "' is defined multiple times.");
    }
    return Optional.empty();
  }

  public static boolean isSetterPresent(
      final String aliasVar,
      final String varTypeName,
      final Scope scope) {
    final String setterName = "set_" + aliasVar;
    final Optional<MethodSymbol> setter = NESTMLSymbols.resolveMethod(
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
