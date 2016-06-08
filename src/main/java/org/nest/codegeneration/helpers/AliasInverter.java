/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTVariable;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

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

  public static boolean isRelativeExpression(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent(), "Run symboltable creator.");
    final Scope scope = astExpr.getEnclosingScope().get();
    boolean isConstantAndVariable = isConstantAndVariable(astExpr);
    if (!isConstantAndVariable) {
      return false;
    }

    final VariableSymbol rightOperand = resolve(astExpr.getRight().get().getVariable().get().toString(), scope);
    boolean isRightParameterTerm = rightOperand.getBlockType().equals(VariableSymbol.BlockType.PARAMETER);
    return isRightParameterTerm;
  }

  private static boolean isConstantAndVariable(ASTExpr astExpr) {
    if (astExpr.getLeft().isPresent()) {
      // the second condition must be checked, because the constant can be in parentheses, e.g. V_reset = ((-10)) + E_L
      boolean numericTerm = !ASTUtils.getAny(astExpr.getLeft().get(), ASTVariable.class).isPresent();
      return numericTerm && astExpr.getRight().isPresent() && astExpr.getRight().get().getVariable().isPresent();

    }
    return false;
  }

  public static boolean isInvertableExpression(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent(), "Run symboltable creator.");
    // todo: check user defined functions
    // check: comparison and relational operations
    if (isAtomicOperand(astExpr))
      return false;

    boolean isInvertableOperation = astExpr.isPlusOp() || astExpr.isMinusOp();
    if (!isInvertableOperation) {
      return false;
    }

    final Scope scope = astExpr.getEnclosingScope().get();
    final VariableSymbol rightOperand = resolve(astExpr.getRight().get().getVariable().get().toString(), scope);
    boolean isRightParameterTerm = rightOperand.getBlockType().equals(VariableSymbol.BlockType.PARAMETER);
    return isRightParameterTerm;
  }

  private static boolean isAtomicOperand(ASTExpr astExpr) {
    boolean isAtomicOperands = astExpr.getLeft().isPresent() && astExpr.getLeft().get().getVariable().isPresent() &&
            astExpr.getRight().isPresent() && astExpr.getRight().get().getVariable().isPresent();

    return !isAtomicOperands;
  }

  public static String inverseOperation(final ASTExpr astExpr) {
    checkArgument(astExpr.isPlusOp() || astExpr.isMinusOp());

    if (astExpr.isPlusOp()) {
      return "-";
    }
    else { // is a '-' operation
      return "+";
    }

  }

  public static VariableSymbol offsetVariable(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent());
    checkArgument(isInvertableExpression(astExpr) || isRelativeExpression(astExpr));

    return resolve(astExpr.getRight().get().getVariable().get().toString(), astExpr.getEnclosingScope().get());
  }

  public static VariableSymbol baseVariable(final ASTExpr astExpr) {
    checkArgument(astExpr.getEnclosingScope().isPresent());
    checkArgument(isInvertableExpression(astExpr));

    return resolve(astExpr.getLeft().get().getVariable().get().toString(), astExpr.getEnclosingScope().get());
  }
}
