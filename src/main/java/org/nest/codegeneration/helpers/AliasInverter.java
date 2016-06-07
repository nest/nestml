/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;

/**
 * Provides methods to compute a setter for a simple alias of the form:
 * a = state_variable + parameter_variable
 * b = constant state_variable/parameter_variable
 *
 * @author plotnikov
 */
public class AliasInverter {

  public static boolean isInvertableExpression(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent(), "Run symboltable creator.");
    // todo: check user defined functions
    // check: comparison and relational operations
    boolean isAtomicOperands =
        astExpr.getLeft().isPresent() && astExpr.getLeft().get().getVariable().isPresent() &&
            astExpr.getRight().isPresent() && astExpr.getRight().get().getVariable().isPresent();
    if (!isAtomicOperands) {
      return false;
    }

    boolean isInvertableOperation = astExpr.isPlusOp() || astExpr.isMinusOp();
    if (!isInvertableOperation) {
      return false;
    }

    final Scope scope = astExpr.getEnclosingScope().get();
    final VariableSymbol rightOperand = resolve(astExpr.getRight().get().getVariable().get().toString(), scope);
    boolean isRightParameterTerm = rightOperand.getBlockType().equals(VariableSymbol.BlockType.PARAMETER);
    return isRightParameterTerm;
  }

  public static String inverseOperation(final ASTExpr astExpr) {
    checkArgument(isInvertableExpression(astExpr));

    if (astExpr.isPlusOp()) {
      return "-";
    }
    else { // is a '-' operation
      return "+";
    }

  }

  public static VariableSymbol offsetVariable(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent());
    checkArgument(isInvertableExpression(astExpr));

    return resolve(astExpr.getRight().get().getVariable().get().toString(), astExpr.getEnclosingScope().get());
  }

  public static VariableSymbol baseVariable(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent());
    checkArgument(isInvertableExpression(astExpr));

    return resolve(astExpr.getLeft().get().getVariable().get().toString(), astExpr.getEnclosingScope().get());
  }
}
