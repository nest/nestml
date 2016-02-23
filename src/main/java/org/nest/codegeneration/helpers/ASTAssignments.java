/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import groovyjarjarantlr.collections.AST;
import org.nest.spl._ast.ASTAssignment;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Computes how the setter call looks like
 *
 * @author plotnikov
 */
@SuppressWarnings("unused") // methods are called from templates
public class ASTAssignments {

  public boolean isCompoundAssignment(final ASTAssignment astAssignment) {
    return astAssignment.isCompoundSum() ||
        astAssignment.isCompoundMinus() ||
        astAssignment.isCompoundProduct() ||
        astAssignment.isCompoundQuotient();
  }

  public String printAssignmentSymbol(final ASTAssignment astAssignment) {
    if (astAssignment.isCompoundSum()) {
      return "+=";
    }
    if (astAssignment.isCompoundMinus()) {
      return "-=";
    }
    if (astAssignment.isCompoundProduct()) {
      return "*=";
    }
    if (astAssignment.isCompoundQuotient()) {
      return "/=";
    }
    return "=";
  }

  /**
   * Checks if the assignment
   */
  public boolean isLocal(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent());
    final Scope scope = astAssignment.getEnclosingScope().get();

    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> variableSymbol = scope.resolve(variableName, VariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the spl variable: " + variableName);

    // TODO does it make sense for the nestml?
    if (variableSymbol.get().getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
      return true;
    }
    else {
      return false;
    }

  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printVariableName(final ASTAssignment astAssignment) {
    return Names.getQualifiedName(astAssignment.getVariableName().getParts());
  }


  /**
   * Returns the textual representation of the setter invocation
   */
  public String printSetterName(final ASTAssignment astAssignment) {
    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    return "set_" + variableName;
  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printGetterName(final ASTAssignment astAssignment) {
    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    return "get_" + variableName;
  }

  public boolean isVector(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent());
    final Scope scope = astAssignment.getEnclosingScope().get();

    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> variableSymbol = scope.resolve(variableName, VariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the spl variable: " + variableName);


    if (variableSymbol.get().getArraySizeParameter().isPresent()) {
      return true;
    }
    // TODO to complex logic, refactor
    final Optional<String> arrayVariable = ASTNodes.getVariablesNamesFromAst(astAssignment.getExpr())
        .stream()
        .filter(
            variableNameInExpression -> {
              final Optional<VariableSymbol> variableSymbolExpr = scope
                  .resolve(variableNameInExpression, VariableSymbol.KIND);
              if ("ext_currents".equals(variableNameInExpression)) {
                System.out.printf("");
              }
              checkState(variableSymbolExpr.isPresent(),
                  "Cannot resolve the spl variable: " + variableNameInExpression);
              if (variableSymbolExpr.get().getArraySizeParameter().isPresent()) {
                return true;
              }
              else {
                return false;
              }
            }
        ).findFirst();

    return arrayVariable.isPresent();
  }

}
