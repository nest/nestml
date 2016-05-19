/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static org.nest.codegeneration.helpers.VariableHelper.printOrigin;

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
      return "set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n" +
          "nest::SpikeEvent se;\n" +
          "network()->send(*this, se, lag);";
    }

    final List<String> callTypes = ASTNodes.getParameterTypes(astFunctionCall);
    final Optional<MethodSymbol> functionSymbol = NESTMLSymbols.resolveMethod(scope, functionName, callTypes);

    if (functionSymbol.isPresent() && functionSymbol.get().getDeclaringType() != null) { // TODO smell

      if (functionSymbol.get().getDeclaringType().getName().equals("Buffer")) {
        final VariableSymbol variableSymbol = resolveVariable(
            Names.getQualifier(functionName), scope);

        if (functionSymbol.get().getName().equals("getSum")) {
          if (variableSymbol.getVectorParameter().isPresent()) {
            final String calleeObject = Names.getQualifier(functionName);
            return "B_." + calleeObject + "_[i].get_value(lag)";
          }
          else {
            final String calleeObject = Names.getQualifier(functionName);
            return "B_." + calleeObject + "_.get_value(lag)";
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
  public String convertNameReference(final ASTVariable astVariable) {
    checkArgument(astVariable.getEnclosingScope().isPresent(), "Run symboltable creator");
    final String variableName = astVariable.toString();
    final Scope scope = astVariable.getEnclosingScope().get();
    if (PredefinedVariables.E_CONSTANT.equals(variableName)) {
      return "numerics::e";
    }
    else {
      final VariableSymbol variableSymbol = VariableSymbol.resolve(variableName, scope);

      if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
        return variableName + (variableSymbol.isVector()?"[i]":"");
      }
      else if(variableSymbol.isBuffer()) {
        return "B_." + variableName + "_.get_value( lag )";
      }
      else {
        if (variableSymbol.isAlias()) {
          return "get_" + variableName + "()" +  (variableSymbol.isVector()?"[i]":"") ;
        }
        else {
          return printOrigin(variableSymbol) + "." + variableName + "_" +  (variableSymbol.isVector()?"[i]":"");
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
