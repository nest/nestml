/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import com.google.common.base.Preconditions;
import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTExpr;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * Compute the type of an expression by an recursive algorithm.
 *
 * @author plotnikov
 */
public class ExpressionTypeCalculator {

  public static final String ERROR_CODE = "SPL_EXPRESSION_TYPE_ERROR";

  public Either<TypeSymbol, String> computeType(final ASTExpr expr) {
    checkNotNull(expr);
    checkArgument(expr.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = expr.getEnclosingScope().get();

    if (expr.leftParenthesesIsPresent()) {
      return computeType(expr.getExpr().get());
    }
    else if (expr.getNumericLiteral().isPresent()) { // number
      if (expr.getNumericLiteral().get() instanceof ASTDoubleLiteral) {
        return Either.left(getRealType());
      }
      else if (expr.getNumericLiteral().get() instanceof ASTIntLiteral) {
        return Either.left(getIntegerType());
      }

    }
    else if(expr.isInf()) {
      return Either.left(getRealType());
    }
    else if (expr.getStringLiteral().isPresent()) { // string
      return Either.left(getStringType());
    }
    else if (expr.getBooleanLiteral().isPresent()) { // boolean
      return Either.left(getBooleanType());
    }
    else if (expr.getQualifiedName().isPresent()) { // var
      final String varName = Names.getQualifiedName(expr.getQualifiedName().get().getParts());
      final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

      if (var.isPresent()) {
        return Either.left(var.get().getType());
      }
      else {
        return Either.right("ExpressionCalculator cannot resolve the type of the variable: " + varName);
      }
    }
    else if (expr.getFunctionCall().isPresent()) { // function
      final String functionName = Names.getQualifiedName(expr.getFunctionCall().get().getQualifiedName().getParts());

      final Optional<MethodSymbol> methodSymbol = scope.resolve(functionName,
          MethodSymbol.KIND);
      if (!methodSymbol.isPresent()) {
        final String msg = "Cannot resolve the method: " + functionName;
        return Either.right(msg);
      }

      if (new TypeChecker().checkVoid(methodSymbol.get().getReturnType())) {
        final String errorMsg = "Function '%s' with returntype 'Void' cannot be used in expressions.";
        Log.error(ERROR_CODE + ":"+ String.format(errorMsg, functionName),
            expr.get_SourcePositionEnd());
      }

      double a = ~1;
      return Either.left(methodSymbol.get().getReturnType());
    }
    else if (expr.isUnaryMinus() || expr.isUnaryPlus()) {
      final Either<TypeSymbol, String> type = computeType(expr.getTerm().get());

      if (type.getLeft().isPresent()) {
        if (isNumeric(type.getLeft().get())) {
          return type;
        }
        else {
          String errorMsg = "Cannot perform a math operation on the not numeric type";
          return Either.right(errorMsg);
        }

      }
    }
    else if (expr.isUnaryTilde()) {
      final Either<TypeSymbol, String> type = computeType(expr.getTerm().get());

      if (type.getLeft().isPresent()) {
        if (isInteger(type.getLeft().get())) {
          return type;
        }
        else {
          String errorMsg = "Cannot perform a math operation on the not numeric type";
          return Either.right(errorMsg);
        }

      }
    }
    else if (expr.isPlusOp()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }
      else {
        // String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string
        if ((lhsType.getLeft().get() == (getStringType()) ||
            rhsType.getLeft().get() == (getStringType())) &&
            (rhsType.getLeft().get() != (getVoidType()) &&
                lhsType.getLeft().get() != (getVoidType()))) {
          return Either.left(getStringType());
        }
        if (isNumeric(lhsType.getLeft().get()) && isNumeric(rhsType.getLeft().get())) {
          // in this case, neither of the sides is a String
          if (lhsType.getLeft().get() == getRealType() ||
              lhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT ||
              rhsType.getLeft().get() == getRealType() ||
              rhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT) {
            return Either.left(getRealType());
          }
          // e.g. both are integers, but check to be sure
          if (lhsType.getLeft().get() == (getIntegerType()) ||
              rhsType.getLeft().get() == (getIntegerType())) {
            return  Either.left(getIntegerType());
          }

          final String errorMsg = "Cannot determine the type of the operation with types: " + lhsType
              + ", " + rhsType + " at " + expr.get_SourcePositionStart() + ">";

          return Either.right(errorMsg);
        }
        // in this case, neither of the sides is a String
        if (lhsType.getLeft().get() == (getRealType()) ||
            rhsType.getLeft().get() == (getRealType())) {
          return Either.left(getRealType());
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.getLeft().get() == (getIntegerType()) ||
            rhsType.getLeft().get() == (getIntegerType())) {
          return  Either.left(getIntegerType());
        }

        // TODO should be not possible
        final String errorMsg = "Cannot determine the type of the Expression-Node @<" + expr.get_SourcePositionStart() +
            ", " + expr.get_SourcePositionStart() + ">";

        return Either.right(errorMsg);
      }

    }
    else if (expr.isMinusOp() || expr.isTimesOp() || expr.isDivOp()) {


      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }

      if (isNumeric(lhsType.getLeft().get()) && isNumeric(rhsType.getLeft().get())) {
        if (lhsType.getLeft().get() == getRealType() ||
            rhsType.getLeft().get() == getRealType() ||
            lhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT ||
            rhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT) {
          return Either.left(getRealType());
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.getLeft().get() == (getIntegerType()) ||
            rhsType.getLeft().get() == (getIntegerType())) {
          return  Either.left(getIntegerType());
        }

        final String errorMsg = "Cannot determine the type of the Expression-Node @<"
            + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();

        return Either.right(errorMsg);
      }
      else {
        final String errorMsg = "Cannot determine the type of the Expression-Node at"
            + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd() ;
        return Either.right(errorMsg);
      }

    }
    else if (expr.isPow()) {
      Preconditions.checkState(expr.getBase().isPresent());
      Preconditions.checkState(expr.getExponent().isPresent());

      final Either<TypeSymbol, String> baseType = computeType(expr.getBase().get());
      final Either<TypeSymbol, String> exponentType = computeType(expr.getExponent().get());

      if (baseType.isRight()) {
        return baseType;
      }
      if (exponentType.isRight()) {
        return exponentType;
      }
      else if (isNumeric(baseType.getLeft().get()) && isNumeric(exponentType.getLeft().get())) {
        if (isInteger(baseType.getLeft().get()) && isInteger(exponentType.getLeft().get())) {
          return Either.left(getIntegerType());
        } else {
          return Either.left(getRealType());
        }
      }
      else {

        final String errorMsg = "Cannot determine the type of the expression." ;
        return Either.right(errorMsg);
      }

    }
    else if (expr.isShiftLeft() ||
        expr.isShiftRight() ||
        expr.isModuloOp() ||
        expr.isBitAnd() ||
        expr.isBitOr() ||
        expr.isBitXor()) {
      Preconditions.checkState(expr.getLeft().isPresent());
      Preconditions.checkState(expr.getRight().isPresent());

      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }
      if (lhsType.getLeft().get() == getIntegerType() &&
          rhsType.getLeft().get() == getIntegerType()) {
        return Either.left(getIntegerType());
      }
      else {
        final String errorMsg = "This operation expects both operands of the type integer in the "
            + "expression" + ASTNodes.toString(expr);
        return Either.right(errorMsg);
      }
    }

    else if (expr.isLt() || expr.isLe() || expr.isEq() || expr.isNe() || expr.isNe2() || expr.isGe() || expr.isGt()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());
      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }

      if (isNumeric(lhsType.getLeft().get()) && isNumeric(rhsType.getLeft().get())) {
        return Either.left(getBooleanType());
      }
      else {
        final String errorMsg = "This operation expects both operands of a numeric type.";

        return Either.right(errorMsg);
      }
    }

    if (expr.getExpr().isPresent()) {
      computeType(expr.getExpr().get());
    }
    else if (expr.isLogicalAnd() || expr.isLogicalOr()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }

      if (isBoolean(lhsType.getLeft().get()) && isBoolean(rhsType.getLeft().get())) {
        return Either.left(getBooleanType());
      }
      else {
        final String errorMsg = "Both operands of the logical expression must be boolean ";
        return Either.right(errorMsg);
      }

    }

    final String errorMsg =  "This operation for expressions is not supported yet.";

    return Either.right(errorMsg);
  }

  /**
   * Checks if the type is a numeric type, e.g. Integer or Real.
   */
  private boolean isNumeric(final TypeSymbol type) {
    return type.equals(getIntegerType()) ||
        type.equals(getRealType()) ||
        type.getType().equals(TypeSymbol.Type.UNIT);

  }

}
