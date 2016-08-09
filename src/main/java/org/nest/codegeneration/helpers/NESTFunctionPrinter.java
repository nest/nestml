/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import org.nest.codegeneration.converters.NESTML2NESTTypeConverter;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTParameter;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTUtils;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Prints regular functions
 *
 * @author plotnikov
 */
@SuppressWarnings("unused") // class is used in templates
public class NESTFunctionPrinter {

  public String printFunctionDeclaration(final ASTFunction astFunction) {
    checkArgument(astFunction.getEnclosingScope().isPresent(), "Function: " + astFunction.getName() + " has no scope.");
    final Scope scope = astFunction.getEnclosingScope().get();

    // TODO names and concept is misleading
    List<String> parameterNestmlTypes = Lists.newArrayList();
    List<String> parameterNestTypes = Lists.newArrayList();
    if (astFunction.getParameters().isPresent()) {
      for (int i = 0; i < astFunction.getParameters().get().getParameters().size(); ++i) {
        String parameterTypeFqn = ASTUtils.computeTypeName(astFunction.getParameters().get().getParameters().get(i).getDatatype());

        Optional<TypeSymbol> parameterType = scope.resolve(parameterTypeFqn, TypeSymbol.KIND);
        checkState(parameterType.isPresent(),
            "Cannot resolve the parameter type: " + parameterTypeFqn + ". In function: " + astFunction
                .getName());
        parameterNestmlTypes.add(parameterTypeFqn);
        parameterNestTypes.add(new NESTML2NESTTypeConverter().convert(parameterType.get()));
      }
    }

    final Optional<MethodSymbol> method = NESTMLSymbols.resolveMethod(
        astFunction.getName(), parameterNestmlTypes, scope
    );

    final StringBuilder declaration = new StringBuilder();
    if (method.isPresent()) {
      declaration.append("//").append(ASTUtils.printComments(astFunction)).append("\n");
      final String returnType = new NESTML2NESTTypeConverter().convert(method.get().getReturnType()).replace(
          ".", "::");
      declaration.append(returnType);
      declaration.append(" ");
      declaration.append(astFunction.getName()).append("(");
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

    // TODO names and concept is misleading
    List<String> parameterNestmlTypes = Lists.newArrayList();
    List<String> parameterNestTypes = Lists.newArrayList();
    if (astFunction.getParameters().isPresent()) {
      for (int i = 0; i < astFunction.getParameters().get().getParameters().size(); ++i) {
        final ASTParameter functionParameter = astFunction.getParameters().get().getParameters().get(i);
        String parameterTypeFqn = ASTUtils.computeTypeName(functionParameter.getDatatype());
        Optional<TypeSymbol> parameterType = scope.resolve(parameterTypeFqn, TypeSymbol.KIND);
        checkState(parameterType.isPresent(),
            "Cannot resolve the parameter type: " + parameterTypeFqn + ". In function: " + astFunction
                .getName());
        parameterNestmlTypes.add(parameterTypeFqn);
        parameterNestTypes.add(new NESTML2NESTTypeConverter().convert(parameterType.get()) + " " + functionParameter.getName()); // TODO misleading name
      }
    }

    final Optional<MethodSymbol> method = NESTMLSymbols.resolveMethod(
        astFunction.getName(), parameterNestmlTypes, scope);

    final StringBuilder declaration = new StringBuilder();
    if (method.isPresent()) {
      declaration.append("//").append(ASTUtils.printComments(astFunction)).append("\n");
      final String returnType = new NESTML2NESTTypeConverter().convert(method.get().getReturnType()).replace(
          ".", "::");
      declaration.append(returnType);
      declaration.append(" ");
      if (!namespace.isEmpty()) {
        declaration.append(namespace).append("::");
      }

      declaration.append(astFunction.getName()).append("(");
      declaration.append(Joiner.on(", ").join(parameterNestTypes));
      declaration.append(")\n");
    }
    else {
      throw new RuntimeException("Cannot resolve the method " + astFunction.getName() + Joiner.on(", ").join(parameterNestmlTypes));
    }
    return declaration.toString();
  }
}
