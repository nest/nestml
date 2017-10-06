/*
 * LegacyExpressionPrinter.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.nest.nestml.prettyprinter;

import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTFunctionCall;

/**
 * Created by ptraeder.
 * "Legacy" version of the expression printer that does not print units for literals
 */
public class LegacyExpressionPrinter extends ExpressionsPrettyPrinter{

  public LegacyExpressionPrinter() {
    super();
  }

  public LegacyExpressionPrinter(final IReferenceConverter referenceConverter) {
    super(referenceConverter);
  }

  @Override
  protected String doPrint(final ASTExpr expr)  {
    if (expr.getNumericLiteral().isPresent()) { // number
      return typesPrinter().prettyprint(expr.getNumericLiteral().get());
    }

    if (expr.isInf()) {
      return convertConstant("inf");
    }
    else if (expr.getStringLiteral().isPresent()) { // string
      return typesPrinter().prettyprint(expr.getStringLiteral().get());
    }
    else if (expr.getBooleanLiteral().isPresent()) { // boolean
      return typesPrinter().prettyprint(expr.getBooleanLiteral().get());
    }
    else if (expr.getVariable().isPresent()) { // var
      return convertVariableName(expr.getVariable().get());
    }
    else if (expr.getFunctionCall().isPresent()) { // function
      final ASTFunctionCall astFunctionCall = expr.getFunctionCall().get();
      return printFunctionCall(astFunctionCall);

    }
    else if (expr.isUnaryPlus()) {
      return "+" + print(expr.getTerm().get());
    }
    else if (expr.isUnaryMinus()) {
      return "-" + print(expr.getTerm().get());
    }
    else if (expr.isUnaryTilde()) {
      return "~" + print(expr.getTerm().get());
    }
    else if (expr.isLeftParentheses() && expr.isRightParentheses()) {
      return "(" + print(expr.getExpr().get()) + ")";
    }
    else if (expr.isPlusOp() || expr.isMinusOp() || expr.isTimesOp() || expr.isDivOp()) {
      final StringBuilder expression = new StringBuilder();
      final String leftOperand = print(expr.getLeft().get());
      final String rightOperand = print(expr.getRight().get());
      expression.append(leftOperand);
      expression.append(getArithmeticOperator(expr));
      expression.append(rightOperand);
      return expression.toString();
    }
    else if (expr.isPow()) {
      final String leftOperand = print(expr.getBase().get());
      final String rightOperand = print(expr.getExponent().get());

      final String powTemplate = referenceConverter.convertBinaryOperator("**");
      return String.format(powTemplate, leftOperand, rightOperand);
    }
    else if (expr.isShiftLeft() ||
        expr.isShiftRight() ||
        expr.isModuloOp() ||
        expr.isBitAnd() ||
        expr.isBitOr() ||
        expr.isBitXor()) {
      final StringBuilder expression = new StringBuilder();
      final String leftOperand = print(expr.getLeft().get());
      final String rightOperand = print(expr.getRight().get());
      expression.append(leftOperand);
      expression.append(printBitOperator(expr));
      expression.append(rightOperand);
      return expression.toString();
    }
    // left:Expr (lt:["<"] | le:["<="] | eq:["=="] | ne:["!="] | ne2:["<>"] | ge:[">="] | gt:[">"]) right:Expr
    else if (expr.isLt() ||
        expr.isLe() ||
        expr.isEq() ||
        expr.isNe() ||
        expr.isNe2() ||
        expr.isGe() ||
        expr.isGt()) {
      final StringBuilder expression = new StringBuilder();
      final String leftOperand = print(expr.getLeft().get());
      final String rightOperand = print(expr.getRight().get());
      expression.append(leftOperand).append(printComparisonOperator(expr)).append(rightOperand);
      return expression.toString();
    }
    else if (expr.isLogicalOr() || expr.isLogicalAnd()) {
      final String leftOperand = print(expr.getLeft().get());
      final String rightOperand = print(expr.getRight().get());

      if (expr.isLogicalAnd()) {
        final String operatorTemplate = referenceConverter.convertBinaryOperator("and");
        return String.format(operatorTemplate, leftOperand, rightOperand);
      }
      else { // it is an or-operator
        final String operatorTemplate = referenceConverter.convertBinaryOperator("or");
        return String.format(operatorTemplate, leftOperand, rightOperand);
      }

    }
    else if (expr.isLogicalNot()) {
      return "not " + print(expr.getExpr().get());
    }
    else if (expr.getCondition().isPresent()) {
      final String condition = print(expr.getCondition().get());
      final String ifTrue = print(expr.getIfTrue().get()); // guaranteed by grammar
      final String ifNot = print(expr.getIfNot().get()); // guaranteed by grammar
      return "(" + condition + ")?(" + ifTrue + "):(" + ifNot + ")";
    }

    final String errorMsg = "Unsupported grammar element:  PrettyPrinter must be fixed " + expr.get_SourcePositionStart();

    throw new RuntimeException(errorMsg);
  }
}
