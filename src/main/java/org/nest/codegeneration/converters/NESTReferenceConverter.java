/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;
import org.nest.spl._ast.ASTFunctionCall;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;
import org.nest.utils.ASTNodes;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Converts constants, names and functions the NEST equivalents.
 *
 * @author plotnikov
 */
public class NESTReferenceConverter implements IReferenceConverter {

  private final PredefinedTypesFactory typesFactory;

  public NESTReferenceConverter(final PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
  }

  @Override
  public String convertBinaryOperator(String binaryOperator) {
    if (binaryOperator.equals("**")) {
      return "pow(%s, %s)";
    }
    if (binaryOperator.equals("and")) {
      return "(%s) && (%s)";
    }
    if (binaryOperator.equals("or")) {
      return "(%s) || (%s)";
    }

    return "(%s)" + binaryOperator + "(%s)";
  }

  @Override
  public String convertFunctionCall(
      final ASTFunctionCall astFunctionCall) {
    checkState(astFunctionCall.getEnclosingScope().isPresent(), "No scope assigned. Run SymbolTable creator.");

    final Scope scope = astFunctionCall.getEnclosingScope().get();
    final String functionName = Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts());

    if ("and".equals(functionName)) {
      return "&&";
    }

    if ("or".equals(functionName)) {
      return "||";
    }

    // Time.resolution() ->
    // nestml::Time::get_resolution().get_ms
    if ("resolution".equals(functionName)) {
      return "nest::Time::get_resolution().get_ms()";
    }
    // Time.steps ->
    // nest::Time(nest::Time::ms( args )).get_steps());
    if ("steps".equals(functionName)) {
      return "nest::Time(nest::Time::ms(%s)).get_steps()";
    }

    if ("pow".equals(functionName)) {
      return "std::pow(%s)";
    }

    if ("exp".equals(functionName)) {
      return "std::exp(%s)";
    }

    if ("expm1".equals(functionName)) {
      return "numerics::expm1(%s)";
    }

    if (functionName.contains("emitSpike")) {
      final String emitStatements = "set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n" +
          "nest::SpikeEvent se;\n" +
          "network()->send(*this, se, lag);";
      return emitStatements;
    }

    final List<String> callTypes = ASTNodes.getArgumentsTypes(astFunctionCall, typesFactory);
    final Optional<NESTMLMethodSymbol> functionSymbol
        = NESTMLSymbols.resolveMethod(scope, functionName, callTypes);
    if (functionSymbol.isPresent() && functionSymbol.get().getDeclaringType() != null) { // TODO smell

      if (functionSymbol.get().getDeclaringType().getName().equals("Buffer")) {
        final NESTMLVariableSymbol variableSymbol = resolveVariable(
            Names.getQualifier(functionName), scope);


        if (functionSymbol.get().getName().equals("getSum")) {
          if (variableSymbol.getArraySizeParameter().isPresent()) {
            final String calleeObject = Names.getQualifier(functionName);
            return "get_" + calleeObject + "()[i].get_value(lag)";
          }
          else {
            final String calleeObject = Names.getQualifier(functionName);
            return "get_" + calleeObject + "().get_value(lag)";
          }

        }

      }

    }

    return functionName;
  }

  private NESTMLVariableSymbol resolveVariable(final String variableName, final Scope scope) {
    final Optional<NESTMLVariableSymbol> variableSymbol = scope.resolve(
        variableName, NESTMLVariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + variableName);
    return variableSymbol.get();
  }

  @Override
  public String convertNameReference(final ASTQualifiedName astQualifiedName) {
    checkArgument(astQualifiedName.getEnclosingScope().isPresent(), "No scope is assigned. Please, build the symbol "
        + "table before calling this function.");
    final String name = Names.getQualifiedName(astQualifiedName.getParts());
    final Scope scope = astQualifiedName.getEnclosingScope().get();
    if ("E".equals(name)) {
      return "numerics::e";
    }
    else {
      final Optional<NESTMLVariableSymbol> variableSymbol = scope.resolve(name, NESTMLVariableSymbol.KIND);

      checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + name);

      if (variableSymbol.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.LOCAL)) {
        return name;
      }
      else {
        if (variableSymbol.get().getArraySizeParameter().isPresent()) {
          return "get_" + name + "()[i]";
        }
        else {
          return "get_" + name + "()";
        }

      }

    }

  }

  @Override
  public String convertConstant(final String constantName) {
    if ("inf".equals(constantName)) {
      return "std::numeric_limits<double_t>::infinity()";
    }
    else {
      return constantName;
    }
  }

  @Override
  public boolean needsArguments(final ASTFunctionCall astFunctionCall) {
    final String functionName = Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts());
    if (functionName.contains("emitSpike")) { // TODO it cannot work!
      return false;
    }
    else {
      return true;
    }
  }

}
