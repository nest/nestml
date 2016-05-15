/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
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


  public String printAssignmentsOperation(final ASTAssignment astAssignment) {
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
    return  "=";
  }

  public String printCompoundOperation(final ASTAssignment astAssignment) {
    if (astAssignment.isCompoundSum()) {
      return "+";
    }
    if (astAssignment.isCompoundMinus()) {
      return "-";
    }
    if (astAssignment.isCompoundProduct()) {
      return "*";
    }
    if (astAssignment.isCompoundQuotient()) {
      return "/";
    }
    throw new RuntimeException("The argument should be a compound assignment.");
  }

  /**
   * Checks if the assignment
   */
  public boolean isLocal(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent());
    final Scope scope = astAssignment.getEnclosingScope().get();

    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final VariableSymbol variableSymbol = VariableSymbol.resolve(variableName, scope);

    return variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL);
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
  public String printLhsName(final ASTAssignment astAssignment) {
    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    return variableName + "_tmp";
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
    final VariableSymbol variableSymbol = VariableSymbol.resolve(variableName, scope);

    if (variableSymbol.getArraySizeParameter().isPresent()) {
      return true;
    }

    // TODO to complex logic, refactor
    final Optional<String> arrayVariable = ASTNodes.getVariablesNamesFromAst(astAssignment.getExpr())
        .stream()
        .filter(variableNameInExpression -> VariableSymbol.resolve(variableNameInExpression, scope)
            .getArraySizeParameter()
            .isPresent()
        ).findFirst();

    return arrayVariable.isPresent();
  }

}
