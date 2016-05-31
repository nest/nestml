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
import org.nest.symboltable.predefined.PredefinedFunctions;
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
import static org.nest.symboltable.symbols.VariableSymbol.resolve;

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

    if (functionName.contains(PredefinedFunctions.EMIT_SPIKE)) {
      return "set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n" +
          "nest::SpikeEvent se;\n" +
          "network()->send(*this, se, lag);";
    }

    final Optional<MethodSymbol> functionSymbol = NESTMLSymbols.resolveMethod(astFunctionCall);

    if (functionSymbol.isPresent() && functionSymbol.get().getDeclaringType() != null) { // TODO smell

      if (functionSymbol.get().getDeclaringType().getName().equals("Buffer")) {
        final VariableSymbol variableSymbol = resolve(Names.getQualifier(functionName), scope);

        if (functionSymbol.get().getName().equals("getSum")) {
          if (variableSymbol.getVectorParameter().isPresent()) {
            final String calleeObject = Names.getQualifier(functionName);
            return "B_." + calleeObject + "[i].get_value(lag)";
          }
          else {
            final String calleeObject = Names.getQualifier(functionName);
            return "B_." + calleeObject + ".get_value(lag)";
          }

        }

      }

    }

    return functionName;
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
      final VariableSymbol variableSymbol = resolve(variableName, scope);

      if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
        return variableName + (variableSymbol.isVector()?"[i]":"");
      }
      else if(variableSymbol.isBuffer()) {
        return "B_." + variableName + ".get_value( lag )";
      }
      else {
        if (variableSymbol.isAlias()) {
          return "get_" + variableName + "()" +  (variableSymbol.isVector()?"[i]":"") ;
        }
        else {
          return printOrigin(variableSymbol) + variableName +  (variableSymbol.isVector()?"[i]":"");
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
    final Optional<MethodSymbol> methodSymbol = NESTMLSymbols.resolveMethod(astFunctionCall);
    checkState(methodSymbol.isPresent(), "Cannot resolve the function call: " + astFunctionCall.getCalleeName());
    return methodSymbol.get().getParameterTypes().size() > 0;
  }

}
