/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTParameter;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.utils.CachedResolver;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Prints regular functions
 *
 * @author plotnikov
 * @since 0.0.1
 */
@SuppressWarnings("unused") // class is used from templates
public class NESTMLFunctionPrinter {

  private final PredefinedTypesFactory typesFactory;

  public NESTMLFunctionPrinter(PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
  }

  public String printFunctionDeclaration(final ASTFunction astFunction) {
    checkArgument(astFunction.getEnclosingScope().isPresent(), "Function: " + astFunction.getName() + " has no scope.");
    final Scope scope = astFunction.getEnclosingScope().get();
    final CachedResolver cachedResolver = new CachedResolver();

    // TODO names and concept is misleading
    List<String> parameterNestmlTypes = Lists.newArrayList();
    List<String> parameterNestTypes = Lists.newArrayList();
    for (int i = 0; i < astFunction.getParameters().get().getParameters().size(); ++i) {
      String parameterTypeFqn = Names.getQualifiedName(astFunction.getParameters().get().getParameters().get(i).getType().getParts());
      Optional<NESTMLTypeSymbol> parameterType = cachedResolver.resolveAndCache(scope, parameterTypeFqn);
      checkState(parameterType.isPresent(),
          "Cannot resolve the parameter type: " + parameterTypeFqn + ". In function: " + astFunction
              .getName());
      parameterNestmlTypes.add(parameterTypeFqn);
      parameterNestTypes.add(new NESTML2NESTTypeConverter(typesFactory).convert(parameterType.get()));
    }

    final Optional<NESTMLMethodSymbol> method = NESTMLSymbols.resolveMethod(scope, astFunction.getName(), parameterNestmlTypes);

    final StringBuilder declaration = new StringBuilder();
    if (method.isPresent()) {
      final String returnType = new NESTML2NESTTypeConverter(typesFactory).convert(method.get().getReturnType()).replace(
          ".", "::");
      declaration.append(returnType);
      declaration.append(" ");
      declaration.append(astFunction.getName() + "(");
      declaration.append(Joiner.on(", ").join(parameterNestTypes));
      declaration.append(")\n");
    }
    else {
      throw new RuntimeException("Cannot resolve the method " + astFunction.getName() + Joiner.on(", ").join(parameterNestmlTypes));
    }
    // TODO
    return declaration.toString();
  }

  public String printFunctionDefinition(final ASTFunction astFunction, final String namespace) {
    checkArgument(astFunction.getEnclosingScope().isPresent(), "Function: " + astFunction.getName() + " has no scope.");
    final Scope scope = astFunction.getEnclosingScope().get();
    final CachedResolver cachedResolver = new CachedResolver();

    // TODO names and concept is misleading
    List<String> parameterNestmlTypes = Lists.newArrayList();
    List<String> parameterNestTypes = Lists.newArrayList();
    for (int i = 0; i < astFunction.getParameters().get().getParameters().size(); ++i) {
      final ASTParameter functionParameter = astFunction.getParameters().get().getParameters().get(i);
      String parameterTypeFqn = Names.getQualifiedName(functionParameter.getType().getParts());
      Optional<NESTMLTypeSymbol> parameterType = cachedResolver.resolveAndCache(scope, parameterTypeFqn);
      checkState(parameterType.isPresent(),
          "Cannot resolve the parameter type: " + parameterTypeFqn + ". In function: " + astFunction
              .getName());
      parameterNestmlTypes.add(parameterTypeFqn);
      parameterNestTypes.add(new NESTML2NESTTypeConverter(typesFactory).convert(parameterType.get()) + " " + functionParameter.getName()); // TODO misleading name
    }

    final Optional<NESTMLMethodSymbol> method = NESTMLSymbols.resolveMethod(scope, astFunction.getName(), parameterNestmlTypes);

    final StringBuilder declaration = new StringBuilder();
    if (method.isPresent()) {
      final String returnType = new NESTML2NESTTypeConverter(typesFactory).convert(method.get().getReturnType()).replace(
          ".", "::");
      declaration.append(returnType);
      declaration.append(" ");
      if (!namespace.isEmpty()) {
        declaration.append(namespace).append("::");
      }

      declaration.append(astFunction.getName() + "(");
      declaration.append(Joiner.on(", ").join(parameterNestTypes));
      declaration.append(")\n");
    }
    else {
      throw new RuntimeException("Cannot resolve the method " + astFunction.getName() + Joiner.on(", ").join(parameterNestmlTypes));
    }
    return declaration.toString();
  }
}
