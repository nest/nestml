/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.spl.prettyprinter.IReferenceConverter;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.utils.ASTUtils.convertDevrivativeNameToSimpleName;
import static org.nest.utils.ASTUtils.convertToSimpleName;

/**
 * Makes a conversion for the GSL solver.
 *
 * @author plotnikov
 */
public class GSLReferenceConverter implements IReferenceConverter {

  private static final String INDEX_VARIABLE_POSTFIX = "_INDEX";
  private static final Double MAXIMAL_EXPONENT = 10.0;

  @Override
  public String convertBinaryOperator(String binaryOperator) {
    if (binaryOperator.equals("**")) {
      return "pow(%s, %s)";
    }
    else {
      return "(%s)" + binaryOperator + "(%s)";
    }
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

    throw new UnsupportedOperationException("Cannot map the function: '" + functionName +"'");
  }

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkState(astVariable.getEnclosingScope().isPresent(), "Run symbol table creator.");
    final String variableName = convertDevrivativeNameToSimpleName(astVariable);
    final Scope scope = astVariable.getEnclosingScope().get();
    final VariableSymbol variableSymbol = VariableSymbol.resolve(convertDevrivativeNameToSimpleName(astVariable), scope);

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
          if (variableSymbol.getVectorParameter().isPresent()) {
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

}
