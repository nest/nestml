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
import static org.nest.spl.symboltable.typechecking.TypeChecker.checkUnit;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
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

    if (expr.isLeftParentheses()) {
      return computeType(expr.getExpr().get());
    }
    if (expr.isUnaryMinus() || expr.isUnaryPlus()) {
      return computeType(expr.getTerm().get());
    }
    else if (expr.getNESTMLNumericLiteral().isPresent()) { // number
      if(expr.getNESTMLNumericLiteral().get().getType().isPresent()) {
        Optional<TypeSymbol> exprType = getTypeIfExists(expr.getNESTMLNumericLiteral().get().getType().get());
        if (exprType.isPresent() && checkUnit(exprType.get())) { //Try Unit Type
          return Either.left(exprType.get());
        }
      }
      else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTDoubleLiteral) {
        return Either.left(getRealType());
      }
      else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
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
    else if (expr.getVariable().isPresent()) { // var
      final String varName = expr.getVariable().get().toString();
      final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

      if (var.isPresent()) {
        return Either.left(var.get().getType());
      }
      else {
        return Either.right("ExpressionCalculator cannot resolve the type of the variable: " + varName);
      }
    }
    else if (expr.getFunctionCall().isPresent()) { // function
      final String functionName = expr.getFunctionCall().get().getCalleeName();

      final Optional<MethodSymbol> methodSymbol = NESTMLSymbols.resolveMethod(expr.getFunctionCall().get());
      if (!methodSymbol.isPresent()) {
        final String msg = "Cannot resolve the method: " + functionName;
        return Either.right(msg);
      }

      if (new TypeChecker().checkVoid(methodSymbol.get().getReturnType())) {
        final String errorMsg = "Function '%s' with returntype 'Void' cannot be used in expressions.";
        Log.error(ERROR_CODE + ":"+ String.format(errorMsg, functionName),
            expr.get_SourcePositionEnd());
      }

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

      final String errorMsg = "Cannot determine the type of the operation with types: " + lhsType
          + ", " + rhsType + " at " + expr.get_SourcePositionStart() + ">";

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
          //both are units
          if (lhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT &&
              rhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT) {
            if(isCompatible(lhsType.getLeft().get(),rhsType.getLeft().get())) {
              return lhsType; //return either of the (same) unit types
            }else{
              return Either.right(errorMsg);
            }
          }
          if (lhsType.getLeft().get() == getRealType() ||
              rhsType.getLeft().get() == getRealType()) {
            return Either.left(getRealType());
          }
          // e.g. both are integers, but check to be sure
          if (lhsType.getLeft().get() == (getIntegerType()) ||
              rhsType.getLeft().get() == (getIntegerType())) {
            return  Either.left(getIntegerType());
          }
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
        return Either.right(errorMsg);
      }

    }
    else if (expr.isMinusOp()) {
      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }

      final String errorMsg = "Cannot determine the type of the Expression-Node @<"
          + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();
      if (isNumeric(lhsType.getLeft().get()) && isNumeric(rhsType.getLeft().get())) {
        //both are units
        if (lhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT &&
            rhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT) {
          if(isCompatible(lhsType.getLeft().get(),rhsType.getLeft().get())) {
            return lhsType; //return either of the (same) unit types
          }
          else{
            return Either.right(errorMsg);
          }
        }
        if (lhsType.getLeft().get() == getRealType() ||
            rhsType.getLeft().get() == getRealType()) {
          return Either.left(getRealType());
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.getLeft().get() == (getIntegerType()) ||
            rhsType.getLeft().get() == (getIntegerType())) {
          return  Either.left(getIntegerType());
        }
        return Either.right(errorMsg);
      }
      else {
        return Either.right(errorMsg);
      }

    }

    else if (expr.isTimesOp() || expr.isDivOp()) {


      final Either<TypeSymbol, String> lhsType = computeType(expr.getLeft().get());
      final Either<TypeSymbol, String> rhsType = computeType(expr.getRight().get());

      if (lhsType.isRight()) {
        return lhsType;
      }
      if (rhsType.isRight()) {
        return rhsType;
      }

      if (isNumeric(lhsType.getLeft().get()) && isNumeric(rhsType.getLeft().get())) {

        // If both are units, calculate resulting Type
        if(lhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT &&
            rhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT){
          UnitRepresentation leftRep = new UnitRepresentation(lhsType.getLeft().get().getName());
          UnitRepresentation rightRep = new UnitRepresentation(rhsType.getLeft().get().getName());
          if(expr.isTimesOp()){
            TypeSymbol returnType = getTypeIfExists((leftRep.multiplyBy(rightRep)).serialize()).get();//Register type on the fly
            return  Either.left(returnType);
          }else if(expr.isDivOp()){
            TypeSymbol returnType = getTypeIfExists((leftRep.divideBy(rightRep)).serialize()).get();//Register type on the fly
            return  Either.left(returnType);
          }
        }
        //if left one is Unit, and the other real or integer, return same Unit
        if (lhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT) {
          return Either.left(lhsType.getLeft().get());
        }
        //if right is Unit and left a number, return right for timesOP and inverted right for DivOp
        if (rhsType.getLeft().get().getType() == TypeSymbol.Type.UNIT) {
          if(expr.isTimesOp()){
            return Either.left(rhsType.getLeft().get());
          }else if(expr.isDivOp()){
            UnitRepresentation rightRep = new UnitRepresentation(rhsType.getLeft().get().getName());
            TypeSymbol returnType = getTypeIfExists((rightRep.invert()).serialize()).get();//Register type on the fly
            return Either.left(returnType);
          }

        }
        //if no Units are involved, Real takes priority
        if(lhsType.getLeft().get() == getRealType() ||
            rhsType.getLeft().get() == getRealType()){
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
        } else if(checkUnit(baseType.getLeft().get())){
            if(!isInteger(exponentType.getLeft().get())){
              return Either.right("With a Unit base, the exponent must be an Integer!");
            }
            UnitRepresentation baseRep = new UnitRepresentation(baseType.getLeft().get().getName());
            Either<Integer, String> numericValue = calculateNumericalValue(expr.getExponent().get());//calculate exponent value if exponent composed of literals
            if(numericValue.isLeft()) {
              return Either.left(getTypeIfExists((baseRep.pow(numericValue.getLeft().get().intValue())).serialize()).get());
            }else{
              return Either.right(numericValue.getRight().get());
            }
        }else{
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
            + "expression" + ASTUtils.toString(expr);
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

      if (isNumeric(lhsType.getLeft().get()) && isNumeric(rhsType.getLeft().get()) ||
          isBoolean(lhsType.getLeft().get()) && isBoolean(rhsType.getLeft().get())) {
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

  private Either<Integer,String> calculateNumericalValue(ASTExpr expr) {
    if (expr.isLeftParentheses()) {
      return calculateNumericalValue(expr.getExpr().get());
    }
    else if (expr.getNESTMLNumericLiteral().isPresent()) {
      if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
        ASTIntLiteral literal = (ASTIntLiteral) expr.getNESTMLNumericLiteral().get().getNumericLiteral();
        return Either.left(literal.getValue());
      }
      else {
        return Either.right("No floating point values allowed in the exponent to a UNIT base");
      }
    }
    else if (expr.isDivOp() || expr.isTimesOp() || expr.isMinusOp() || expr.isPlusOp()) {
      Either<Integer, String> lhs = calculateNumericalValue(expr.getLeft().get());
      Either<Integer, String> rhs = calculateNumericalValue(expr.getRight().get());
      if (lhs.isRight()) {
        return lhs;
      }
      if (rhs.isRight()) {
        return rhs;
      }
      if (expr.isDivOp())
        return Either.left(lhs.getLeft().get().intValue() / rhs.getLeft().get().intValue()); //int division!
      if (expr.isTimesOp())
        return Either.left(lhs.getLeft().get().intValue() * rhs.getLeft().get().intValue());
      if (expr.isPlusOp())
        return Either.left(lhs.getLeft().get().intValue() + rhs.getLeft().get().intValue());
      if (expr.isMinusOp())
        return Either.left(lhs.getLeft().get().intValue() - rhs.getLeft().get().intValue());
    }
    else if (expr.isPow()) {
      Either<Integer, String> base = calculateNumericalValue(expr.getBase().get());
      Either<Integer, String> exponent = calculateNumericalValue(expr.getExponent().get());
      if (base.isRight()) {
        return base;
      }
      if (exponent.isRight()) {
        return exponent;
      }
      return Either.left((int) Math.pow(base.getLeft().get().intValue(), exponent.getLeft().get().intValue()));
    }
    else if (expr.isUnaryMinus()) {
      Either<Integer, String> term = calculateNumericalValue(expr.getTerm().get());
      if (term.isRight()) {
        return term;
      }
      return Either.left(-term.getLeft().get().intValue());
    }

    return Either.right("Cannot calculate value of exponent. Must be a static value!");
  }
  /**
   * Checks if the type is a numeric type, e.g. Integer or Real.
   */
  private boolean isBoolean(final TypeSymbol type) {
    return type.equals(getBooleanType());

  }

}
