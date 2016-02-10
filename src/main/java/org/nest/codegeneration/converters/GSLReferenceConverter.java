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
import org.nest.spl._ast.ASTVariable;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;
import org.nest.utils.NESTMLSymbols;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Makes a conversion for the GSL solver.
 *
 * @author plotnikov
 */
public class GSLReferenceConverter implements IReferenceConverter {

  public static final String INDEX_VARIABLE_POSTFIX = "_INDEX";

  private static final Double MAXIMAL_EXPONENT = 10.0;

  @Override
  public String convertBinaryOperator(String binaryOperator) {
    return "(%s)" + binaryOperator + "(%s)";
  }

  @Override
  public String convertFunctionCall(final ASTFunctionCall astFunctionCall) {
    final String functionName = astFunctionCall.getCalleeName();
    if ("exp".equals(functionName)) {
      return "std::exp(std::min(%s, " + MAXIMAL_EXPONENT + "))";
    }
    if ("pow".equals(functionName)) {
      return "pow(%s)";
    }
    throw new UnsupportedOperationException();
  }

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkState(astVariable.getEnclosingScope().isPresent(), "Run symbol table creator.");
    final String variableName = astVariable.toString();
    final VariableSymbol variableSymbol
        = resolveVariable(variableName, astVariable.getEnclosingScope().get());
    if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.STATE) &&
        !variableSymbol.isAlias()) {
      return "y[" + variableName + INDEX_VARIABLE_POSTFIX + "]";
    }
    else {

      if (PredefinedVariables.E_CONSTANT.equals(variableName)) {
        return "numerics::e";
      }
      else {
        if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL) ||
            variableSymbol.isAlias()) {
          return variableName;
        }
        else {
          if (variableSymbol.getArraySizeParameter().isPresent()) {
            return "node.get_" + variableName + "()[i]";
          }
          else {
            return "node.get_" + variableName + "()";
          }

        }

      }

    }
  }

  @Override
  public String convertConstant(final String constantName) {
    return constantName;
  }

  @Override
  public boolean needsArguments(final ASTFunctionCall astFunctionCall) {
    final String functionName = astFunctionCall.getCalleeName();
    if ("exp".equals(functionName)) {
      return true;
    }
    if ("pow".equals(functionName)) {
      return true;
    }
    throw new UnsupportedOperationException();
  }

  private VariableSymbol resolveVariable(final String variableName, final Scope scope) {
    final Optional<VariableSymbol> variableSymbol = NESTMLSymbols.resolve(variableName, scope);
    checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + variableName);
    return variableSymbol.get();
  }
}
