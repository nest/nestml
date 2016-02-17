/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.spl._ast.ASTFunctionCall;
import org.nest.spl._ast.ASTVariable;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
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

  @Override
  public String convertBinaryOperator(final String binaryOperator) {
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
  public String convertFunctionCall(final ASTFunctionCall astFunctionCall) {
    checkState(astFunctionCall.getEnclosingScope().isPresent(), "No scope assigned. Run SymbolTable creator.");

    final Scope scope = astFunctionCall.getEnclosingScope().get();
    final String functionName = astFunctionCall.getCalleeName();

    if ("and".equals(functionName)) {
      return "&&";
    }

    if ("or".equals(functionName)) {
      return "||";
    }
    // Time.resolution() -> nestml::Time::get_resolution().get_ms
    if ("resolution".equals(functionName)) {
      return "nest::Time::get_resolution().get_ms()";
    }
    // Time.steps -> nest::Time(nest::Time::ms( args )).get_steps());
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

    final List<String> callTypes = ASTNodes.getArgumentsTypes(astFunctionCall);
    final Optional<MethodSymbol> functionSymbol
        = NESTMLSymbols.resolveMethod(scope, functionName, callTypes);
    if (functionSymbol.isPresent() && functionSymbol.get().getDeclaringType() != null) { // TODO smell

      if (functionSymbol.get().getDeclaringType().getName().equals("Buffer")) {
        final VariableSymbol variableSymbol = resolveVariable(
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

  private VariableSymbol resolveVariable(final String variableName, final Scope scope) {
    final Optional<VariableSymbol> variableSymbol = scope.resolve(
        variableName, VariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + variableName);
    return variableSymbol.get();
  }

  @Override
  public String convertNameReference(final ASTVariable astQualifiedName) {
    checkArgument(astQualifiedName.getEnclosingScope().isPresent(), "No scope is assigned. Please, build the symbol "
        + "table before calling this function.");
    final String name = astQualifiedName.toString();
    final Scope scope = astQualifiedName.getEnclosingScope().get();
    if (PredefinedVariables.E_CONSTANT.equals(name)) {
      return "numerics::e";
    }
    else {
      final Optional<VariableSymbol> variableSymbol = scope.resolve(name, VariableSymbol.KIND);

      if (!variableSymbol.isPresent()) {
        scope.resolve(name, VariableSymbol.KIND);
      }
      checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + name);

      if (variableSymbol.get().getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
        return name;
      }
      else if(variableSymbol.get().getBlockType() == VariableSymbol.BlockType.INPUT_BUFFER_CURRENT ||
          variableSymbol.get().getBlockType() == VariableSymbol.BlockType.INPUT_BUFFER_CURRENT) {
        return "get_" + name + "().get_value( lag )";
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
    final String functionName = astFunctionCall.getCalleeName();
    if (functionName.contains("emitSpike")) { // TODO it cannot work!
      return false;
    }
    else {
      return true;
    }
  }

}
