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
import static org.nest.symboltable.symbols.VariableSymbol.resolve;

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

  public String printOrigin(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "Run symbol table creator.");
    final Scope scope = astAssignment.getEnclosingScope().get();
    return VariableHelper.printOrigin(resolve(astAssignment.getLhsVarialbe(), scope));
  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printLHS(final ASTAssignment astAssignment) {

    return astAssignment.getLhsVarialbe();
  }


  /**
   * Returns the textual representation of the setter invocation
   */
  public String printSetterName(final ASTAssignment astAssignment) {
    return "set_" + astAssignment.getLhsVarialbe();
  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printLhsName(final ASTAssignment astAssignment) {
    return astAssignment.getLhsVarialbe() + "_tmp";
  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printGetterName(final ASTAssignment astAssignment) {
    final String variableName = astAssignment.getLhsVarialbe();
    return "get_" + variableName;
  }

  public boolean isVector(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent());
    final Scope scope = astAssignment.getEnclosingScope().get();

    final String variableName = astAssignment.getLhsVarialbe();
    final VariableSymbol variableSymbol = resolve(variableName, scope);

    if (variableSymbol.getVectorParameter().isPresent()) {
      return true;
    }

    // TODO to complex logic, refactor
    final Optional<String> arrayVariable = ASTNodes.getVariablesNamesFromAst(astAssignment.getExpr())
        .stream()
        .filter(variableNameInExpression -> resolve(variableNameInExpression, scope)
            .getVectorParameter()
            .isPresent()
        ).findFirst();

    return arrayVariable.isPresent();
  }

  public boolean isVectorLHS(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "No scope. Run symbol table creator");
    final Scope scope = astAssignment.getEnclosingScope().get();
    final String lhsVarName = astAssignment.getLhsVarialbe();
    final VariableSymbol lhsVarSymbol = resolve(lhsVarName, scope);

    return lhsVarSymbol.getVectorParameter().isPresent();
  }

  public String printSizeParameter(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "Run symbol table creator");
    final Scope scope = astAssignment.getEnclosingScope().get();

    Optional<VariableSymbol> vectorVariable = ASTNodes.getVariableSymbols(astAssignment.getExpr())
        .stream()
        .filter(VariableSymbol::isVector).findAny();
    if (!vectorVariable.isPresent()) {
      vectorVariable = Optional.of(resolve(astAssignment.getLhsVarialbe(), astAssignment.getEnclosingScope().get()));
    }
    // The existence of the variable is ensured by construction
    return vectorVariable.get().getVectorParameter().get(); // Array parameter is ensured by the query
  }
}
