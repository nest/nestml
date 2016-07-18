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
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.ASTUtils;
import org.nest.utils.NESTMLSymbols;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
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

    if (expr.isLeftParentheses()) {
      return computeType(expr.getExpr().get());
    }
    else if (expr.isUnaryMinus() || expr.isUnaryPlus()) {
      return computeType(expr.getTerm().get());
    }
    else if (expr.getNESTMLNumericLiteral().isPresent()) { // number
      if (expr.getNESTMLNumericLiteral().get().getType().isPresent()) {
        Optional<TypeSymbol> exprType = getTypeIfExists(expr.getNESTMLNumericLiteral().get().getType().get());
        if (exprType.isPresent() && checkUnit(exprType.get())) { //Try Unit Type
          return Either.value(exprType.get());
        }
      }
      else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTDoubleLiteral) {
        return Either.value(getRealType());
      }
      else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
        return Either.value(getIntegerType());
      }
    }
    else if (expr.isInf()) {
      return Either.value(getRealType());
    }
    else if (expr.getStringLiteral().isPresent()) { // string
      return Either.value(getStringType());
    }
    else if (expr.getBooleanLiteral().isPresent()) { // boolean
      return Either.value(getBooleanType());
    }
    else if (expr.getVariable().isPresent()) { // var
      final String varName = expr.getVariable().get().toString();
      final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

      if (var.isPresent()) {
        return Either.value(var.get().getType());
      }
      else {
        return Either.error("ExpressionCalculator cannot resolve the type of the variable: " + varName);
      }
    }
    else if (expr.getFunctionCall().isPresent()) { // function
      final String functionName = expr.getFunctionCall().get().getCalleeName();

      final Optional<MethodSymbol> methodSymbol = NESTMLSymbols.resolveMethod(expr.getFunctionCall().get());
      if (!methodSymbol.isPresent()) {
        final String msg = "Cannot resolve the method: " + functionName;
        return Either.error(msg);
      }

      if (new TypeChecker().checkVoid(methodSymbol.get().getReturnType())) {
        final String errorMsg = "Function '%s' with returntype 'Void' cannot be used in expressions.";
        Log.error(ERROR_CODE + ":" + String.format(errorMsg, functionName),
            expr.get_SourcePositionEnd());
      }

      return Either.value(methodSymbol.get().getReturnType());
    }
    else if (expr.isUnaryMinus() || expr.isUnaryPlus()) {
      final Either<TypeSymbol, String> type = computeType(expr.getTerm().get());

      if (type.isValue()) {
        if (isNumeric(type.getValue())) {
          return type;
        }
        else {
          String errorMsg = "Cannot perform a math operation on the not numeric type";
          return Either.error(errorMsg);
        }

      }
    }
    else if (expr.isUnaryTilde()) {
      final Either<TypeSymbol, String> type = computeType(expr.getTerm().get());

      if (type.isValue()) {
        if (isInteger(type.getValue())) {
          return type;
        }
        else {
          String errorMsg = "Cannot perform a math operation on the not numeric type";
          return Either.error(errorMsg);
        }

      }
    }
    else if (expr.isPlusOp()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      final String errorMsg = "Cannot determine the type of the operation with types: " + lhsType
                              + ", " + rhsType + " at " + expr.get_SourcePositionStart() + ">";

      if (lhsType.isError()) {
        return lhsType;
      }
      if (rhsType.isError()) {
        return rhsType;
      }
      else { // checked that both are vaules
        // String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string
        if ((lhsType.getValue() == (getStringType()) ||
             rhsType.getValue() == (getStringType())) &&
            (rhsType.getValue() != (getVoidType()) && lhsType.getValue() != (getVoidType()))) {
          return Either.value(getStringType());
        }
        if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue())) {
          // in this case, neither of the sides is a String
          //both are units
          if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT &&
              rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
            if (isCompatible(lhsType.getValue(), rhsType.getValue())) {
              return lhsType; //return either of the (same) unit types
            }
            else {
              return Either.error(errorMsg);
            }
          }
          if (lhsType.getValue() == getRealType() || rhsType.getValue() == getRealType()) {
            return Either.value(getRealType());
          }
          // e.g. both are integers, but check to be sure
          if (lhsType.getValue() == (getIntegerType()) || rhsType.getValue() == (getIntegerType())) {
            return Either.value(getIntegerType());
          }
          return Either.error(errorMsg);
        }
        // in this case, neither of the sides is a String
        if (lhsType.getValue() == (getRealType()) || rhsType.getValue() == (getRealType())) {
          return Either.value(getRealType());
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.getValue() == (getIntegerType()) || rhsType.getValue() == (getIntegerType())) {
          return Either.value(getIntegerType());
        }

        // TODO should be not possible
        return Either.error(errorMsg);
      }

    }
    else if (expr.isMinusOp()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isError()) {
        return lhsType;
      }
      if (rhsType.isError()) {
        return rhsType;
      }

      // from here both types are computed and available
      final String errorMsg = "Cannot determine the type of the Expression-Node @<"
                              + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();
      if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue())) {
        //both are units
        if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT &&
            rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          if (isCompatible(lhsType.getValue(), rhsType.getValue())) {
            return lhsType; //return either of the (same) unit types
          }
          else {
            return Either.error(errorMsg);
          }
        }
        if (lhsType.getValue() == getRealType() ||
            rhsType.getValue() == getRealType()) {
          return Either.value(getRealType());
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.getValue() == (getIntegerType()) || rhsType.getValue() == (getIntegerType())) {
          return Either.value(getIntegerType());
        }
        return Either.error(errorMsg);
      }
      else {
        return Either.error(errorMsg);
      }

    }
    else if (expr.isTimesOp() || expr.isDivOp()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isError()) {
        return lhsType;
      }
      if (rhsType.isError()) {
        return rhsType;
      }

      if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue())) {

        // If both are units, calculate resulting Type
        if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT && rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          UnitRepresentation leftRep = new UnitRepresentation(lhsType.getValue().getName());
          UnitRepresentation rightRep = new UnitRepresentation(rhsType.getValue().getName());
          if (expr.isTimesOp()) {
            TypeSymbol returnType = getTypeIfExists((leftRep.multiplyBy(rightRep)).serialize()).get();//Register type on the fly
            return Either.value(returnType);
          }
          else if (expr.isDivOp()) {
            TypeSymbol returnType = getTypeIfExists((leftRep.divideBy(rightRep)).serialize()).get();//Register type on the fly
            return Either.value(returnType);
          }
        }
        //if value one is Unit, and the other real or integer, return same Unit
        if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          return Either.value(lhsType.getValue());
        }
        //if error is Unit and value a number, return error for timesOP and inverted error for DivOp
        if (rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          if (expr.isTimesOp()) {
            return Either.value(rhsType.getValue());
          }
          else if (expr.isDivOp()) {
            UnitRepresentation rightRep = new UnitRepresentation(rhsType.getValue().getName());
            TypeSymbol returnType = getTypeIfExists((rightRep.invert()).serialize()).get();//Register type on the fly
            return Either.value(returnType);
          }

        }
        //if no Units are involved, Real takes priority
        if (lhsType.getValue() == getRealType() || rhsType.getValue() == getRealType()) {
          return Either.value(getRealType());
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.getValue() == getIntegerType() || rhsType.getValue() == getIntegerType()) {
          return Either.value(getIntegerType());
        }

        final String errorMsg = "Cannot determine the type of the Expression-Node @<"
                                + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();

        return Either.error(errorMsg);
      }
      else {

        final String errorMsg = "Cannot determine the type of the Expression-Node at"
                                + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();
        return Either.error(errorMsg);
      }

    }
    else if (expr.isPow()) {
      Preconditions.checkState(expr.getBase().isPresent());
      Preconditions.checkState(expr.getExponent().isPresent());

      final Either<TypeSymbol, String> baseType = computeType(expr.getBase().get());
      final Either<TypeSymbol, String> exponentType = computeType(expr.getExponent().get());

      if (baseType.isError()) {
        return baseType;
      }
      if (exponentType.isError()) {
        return exponentType;
      }
      else if (isNumeric(baseType.getValue()) && isNumeric(exponentType.getValue())) {
        if (isInteger(baseType.getValue()) && isInteger(exponentType.getValue())) {
          return Either.value(getIntegerType());
        }
        else if (checkUnit(baseType.getValue())) {
          if (!isInteger(exponentType.getValue())) {
            return Either.error("With a Unit base, the exponent must be an Integer!");
          }
          UnitRepresentation baseRep = new UnitRepresentation(baseType.getValue().getName());
          Either<Integer, String> numericValue = calculateNumericalValue(expr.getExponent().get());//calculate exponent value if exponent composed of literals
          if (numericValue.isValue()) {
            return Either.value(getTypeIfExists((baseRep.pow(numericValue.getValue())).serialize()).get());
          }
          else {
            return Either.error(numericValue.getError());
          }
        }
        else {
          return Either.value(getRealType());
        }
      }
      else {
        final String errorMsg = "Cannot determine the type of the expression.";
        return Either.error(errorMsg);
      }

    }
    else if (expr.isEq() ) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());
      if (lhsType.isError()) {
        return lhsType;
      }
      if (rhsType.isError()) {
        return rhsType;
      }

      if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue()) ||
          isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
        return Either.value(getBooleanType());
      }
      else {
        final String errorMsg = "Only variables of the same type can be checked for the equality. And not: " +
            lhsType.getValue() + " and " + rhsType.getValue();

        return Either.error(errorMsg);
      }
    }
    else if (expr.isLt() || expr.isLe() || expr.isNe() || expr.isNe2() || expr.isGe() || expr.isGt()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());
      if (lhsType.isError()) {
        return lhsType;
      }
      if (rhsType.isError()) {
        return rhsType;
      }

      if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue()) ||
          isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
        return Either.value(getBooleanType());
      }
      else {
        final String errorMsg = "This operation expects both operands of a numeric type.";

        return Either.error(errorMsg);
      }
    }
    else if (expr.isLogicalNot()) {
      final Either<TypeSymbol, String> type = computeType(expr.getExpr().get());
      if (type.isError()) {
        return type;
      }
      else if (isBoolean(type.getValue())) {
        return Either.value(getBooleanType());
      }
      else {
        return Either.error("Logical 'not' expects an boolean type and not: " + type.getValue());
      }
    }
    else if (expr.isLogicalAnd() || expr.isLogicalOr()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isError()) {
        return lhsType;
      }
      if (rhsType.isError()) {
        return rhsType;
      }

      if (isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
        return Either.value(getBooleanType());
      }
      else {
        final String errorMsg = "Both operands of the logical expression must be boolean ";
        return Either.error(errorMsg);
      }

    }
    else if (expr.getCondition().isPresent()) {

      final Either<TypeSymbol, String> condition = computeType(expr.getCondition().get());
      final Either<TypeSymbol, String> ifTrue = computeType(expr.getIfTure().get()); // guaranteed by the grammar
      final Either<TypeSymbol, String> ifNot = computeType(expr.getIfNot().get()); // guaranteed by the grammar

      if (condition.isError()) {
        return condition;
      }
      if (ifTrue.isError()) {
        return ifTrue;
      }

      if (ifNot.isError()) {
        return ifNot;
      }
      if (!condition.getValue().equals(getBooleanType())) {
        return Either.error("The ternary operator condition must be a boolean: " + ASTUtils.toString(expr) + ".  And not a: " + condition.getValue());
      }
      if (!isCompatible(ifTrue.getValue(), (ifNot.getValue()))) {
        return Either.error("The ternary operator results must be of the same type: " + ASTUtils.toString(expr) + ".  And not: " + ifTrue.getValue() + " and " + ifNot.getValue());
      }
      return ifTrue;
    }

    final String errorMsg = "This operation for expressions is not supported yet.";

    return Either.error(errorMsg);
  }

  /**
   * Checks if the type is a numeric type, e.g. Integer or Real.
   */
  private boolean isNumeric(final TypeSymbol type) {
    return type.equals(getIntegerType()) ||
           type.equals(getRealType()) ||
           type.getType().equals(TypeSymbol.Type.UNIT);

  }

  private Either<Integer, String> calculateNumericalValue(ASTExpr expr) {
    if (expr.isLeftParentheses()) {
      return calculateNumericalValue(expr.getExpr().get());
    }
    else if (expr.getNESTMLNumericLiteral().isPresent()) {
      if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
        ASTIntLiteral literal = (ASTIntLiteral) expr.getNESTMLNumericLiteral().get().getNumericLiteral();
        return Either.value(literal.getValue());
      }
      else {
        return Either.error("No floating point values allowed in the exponent to a UNIT base");
      }
    }
    else if (expr.isDivOp() || expr.isTimesOp() || expr.isMinusOp() || expr.isPlusOp()) {
      Either<Integer, String> lhs = calculateNumericalValue(expr.getLeft().get());
      Either<Integer, String> rhs = calculateNumericalValue(expr.getRight().get());
      if (lhs.isError()) {
        return lhs;
      }
      if (rhs.isError()) {
        return rhs;
      }
      if (expr.isDivOp()) {
        return Either.value(lhs.getValue() / rhs.getValue()); //int division!
      }
      if (expr.isTimesOp()) {
        return Either.value(lhs.getValue() * rhs.getValue());
      }
      if (expr.isPlusOp()) {
        return Either.value(lhs.getValue() + rhs.getValue());
      }
      if (expr.isMinusOp()) {
        return Either.value(lhs.getValue() - rhs.getValue());
      }
    }
    else if (expr.isPow()) {
      Either<Integer, String> base = calculateNumericalValue(expr.getBase().get());
      Either<Integer, String> exponent = calculateNumericalValue(expr.getExponent().get());
      if (base.isError()) {
        return base;
      }
      if (exponent.isError()) {
        return exponent;
      }
      return Either.value((int) Math.pow(base.getValue(), exponent.getValue()));
    }
    else if (expr.isUnaryMinus()) {
      Either<Integer, String> term = calculateNumericalValue(expr.getTerm().get());
      if (term.isError()) {
        return term;
      }
      return Either.value(-term.getValue());
    }

    return Either.error("Cannot calculate value of exponent. Must be a static value!");
  }

  /**
   * Checks if the type is a numeric type, e.g. Integer or Real.
   */
  private boolean isBoolean(final TypeSymbol type) {
    return type.equals(getBooleanType());

  }

}
