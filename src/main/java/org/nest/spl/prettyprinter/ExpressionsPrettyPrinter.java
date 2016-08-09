/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.prettyprinter;

import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;

import java.util.List;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * Converts SPL expressions to the executable platform dependent code. By using different
 * referenceConverters the handling of variables, names, and functions can be adapted. For this,
 * implement own {@code IReferenceConverter} specialisation.
 *
 * @author plotnikov
 */
public class ExpressionsPrettyPrinter {

  private final IReferenceConverter referenceConverter;

  public ExpressionsPrettyPrinter() {
    this.referenceConverter = new IdempotentReferenceConverter();
  }

  public ExpressionsPrettyPrinter(final IReferenceConverter referenceConverter) {
    this.referenceConverter = referenceConverter;
  }

  public String print(final ASTExpr expr) {
    checkNotNull(expr);
    return doPrint(expr);
  }

  private String doPrint(final ASTExpr expr) {
    if (expr.getNESTMLNumericLiteral().isPresent()) { // number
      return typesPrinter().prettyprint(expr.getNESTMLNumericLiteral().get().getNumericLiteral());
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
      return printMethodCall(astFunctionCall);

    }
    else if (expr.isUnaryPlus()) {
      return "(" + "+" + print(expr.getTerm().get()) + ")";
    }
    else if (expr.isUnaryMinus()) {
      return "(" + "-" + print(expr.getTerm().get()) + ")";
    }
    else if (expr.isUnaryTilde()) {
      return "(" + "~" + print(expr.getTerm().get()) + ")";
    }
    else if (expr.isLeftParentheses() && expr.isRightParentheses()) {
      return "(" +  print(expr.getExpr().get()) + ")";
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
      final String ifTrue = print(expr.getIfTure().get()); // guaranteed by grammar
      final String ifNot = print(expr.getIfNot().get()); // guaranteed by grammar
      return "(" + condition + ")?(" + ifTrue + "):(" + ifNot + ")";
    }

    final String errorMsg = "Unsupported grammar element:  PrettyPrinter must be fixed " + expr.get_SourcePositionStart();

    throw new RuntimeException(errorMsg);
  }

  /**
   * This method must be public, since it is used in Freemarker template
   */
  public String printMethodCall(final ASTFunctionCall astFunctionCall) {
    final String nestFunctionName = referenceConverter.convertFunctionCall(astFunctionCall);

    if (referenceConverter.needsArguments(astFunctionCall)) {
      final StringBuilder argsListAsString = printFunctionCallArguments(astFunctionCall);
      return String.format(nestFunctionName, argsListAsString);
    }
    else {
      return nestFunctionName;
    }
  }

  /**
   * This method must be public, since it is used in Freemarker template
   */
  private StringBuilder printFunctionCallArguments(final ASTFunctionCall astFunctionCall) {
    final StringBuilder argsListAsString = new StringBuilder();

    final List<ASTExpr> functionArgs = astFunctionCall.getArgs();
    for (int i = 0; i < functionArgs.size(); ++i) {
      boolean isLastArgument = (i+1) == functionArgs.size();
      if (!isLastArgument) {
        argsListAsString.append(print(functionArgs.get(i)));
        argsListAsString.append(", ");
      }
      else {
        // last argument, don't append ','
        argsListAsString.append(print(functionArgs.get(i)));
      }

    }
    return argsListAsString;
  }

  private String convertConstant(final String constantName) {
    return referenceConverter.convertConstant(constantName);
  }

  private String convertVariableName(final ASTVariable astVariableName) {
    return referenceConverter.convertNameReference(astVariableName);
  }

  private String printComparisonOperator(final ASTExpr expr) {
    if (expr.isLt()) {
      return "<";
    }
    if (expr.isLe()) {
      return "<=";
    }
    if (expr.isEq()) {
      return "==";
    }
    if (expr.isNe() || expr.isNe2()) {
      return "!=";
    }
    if (expr.isGe()) {
      return ">=";
    }
    if (expr.isGt()) {
      return ">";
    }
    throw new RuntimeException("Cannot determine comparison operator");
  }

  private String printBitOperator(final ASTExpr expr) {
    if (expr.isShiftLeft()) {
      return "<<";
    }
    if (expr.isShiftRight()) {
      return ">>";
    }
    if (expr.isModuloOp()) {
      return "%";
    }
    if (expr.isBitAnd()) {
      return "&";
    }
    if (expr.isBitOr()) {
      return "|";
    }
    if (expr.isBitXor()) {
      return "^";
    }

    throw new RuntimeException("Cannot determine mathematical operator");
  }

  private String getArithmeticOperator(final ASTExpr expr) {
    if (expr.isPlusOp()) {
      return "+";
    }
    if(expr.isMinusOp()) {
      return "-";
    }
    if (expr.isTimesOp()) {
      return "*";
    }
    if (expr.isDivOp()) {
      return "/";
    }
    throw new RuntimeException("Cannot determine mathematical operator");
  }

  private TypesPrettyPrinterConcreteVisitor typesPrinter() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }
}
