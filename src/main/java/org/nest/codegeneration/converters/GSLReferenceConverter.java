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
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Makes a conversion for the GSL solver.
 *
 * @author plotnikov
 */
public class GSLReferenceConverter implements IReferenceConverter {

  @Override
  public String convertBinaryOperator(String binaryOperator) {
    return "(%s)" + binaryOperator + "(%s)";
  }

  @Override
  public String convertFunctionCall(final ASTFunctionCall astFunctionCall) {
    throw new UnsupportedOperationException();
  }

  @Override
  public String convertNameReference(final ASTQualifiedName astQualifiedName) {
    checkState(astQualifiedName.getEnclosingScope().isPresent(), "Run symbol table creator.");
    final String variableName = Names.getQualifiedName(astQualifiedName.getParts());
    final NESTMLVariableSymbol variableSymbol
        = resolveVariable(variableName, astQualifiedName.getEnclosingScope().get());
    if (variableSymbol.getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE)) {
      return "y[" + variableName + "_index" + "]";
    }
    else {

      if ("E".equals(variableName)) {
        return "numerics::e";
      }
      else {
        if (variableSymbol.getBlockType().equals(NESTMLVariableSymbol.BlockType.LOCAL)) {
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
    throw new UnsupportedOperationException();
  }

  private NESTMLVariableSymbol resolveVariable(final String variableName, final Scope scope) {
    final Optional<NESTMLVariableSymbol> variableSymbol = scope.resolve(
        variableName, NESTMLVariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + variableName);
    return variableSymbol.get();
  }
}
