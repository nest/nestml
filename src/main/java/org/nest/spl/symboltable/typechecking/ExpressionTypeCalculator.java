/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import com.google.common.base.Preconditions;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.spl.prettyprinter.SPLPrettyPrinter;
import org.nest.spl.prettyprinter.SPLPrettyPrinterFactory;
import org.nest.spl._ast.ASTExpr;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.symboltable.predefined.PredefinedTypes;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Compute the type of an expression by an recursive algorithm.
 *
 * @author plotnikov
 * @since 0.0.1
 */
public class ExpressionTypeCalculator {

  public static final String ERROR_CODE = "SPL_EXPRESSION_TYPE_ERROR";

  public TypeSymbol computeType(final ASTExpr expr) {
    Preconditions.checkNotNull(expr);
    checkArgument(expr.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = expr.getEnclosingScope().get();

    if (expr.leftParenthesesIsPresent()) {
      return computeType(expr.getExpr().get());
    }
    else if (expr.getNumericLiteral().isPresent()) { // number
      if (expr.getNumericLiteral().get() instanceof ASTDoubleLiteral) {
        return PredefinedTypes.getRealType();
      }
      else if (expr.getNumericLiteral().get() instanceof ASTIntLiteral) {
        return PredefinedTypes.getIntegerType();
      }

    }
    else if(expr.isInf()) {
      return PredefinedTypes.getRealType();
    }
    else if (expr.getStringLiteral().isPresent()) { // string
      return PredefinedTypes.getStringType();
    }
    else if (expr.getBooleanLiteral().isPresent()) { // boolean
      return PredefinedTypes.getBooleanType();
    }
    else if (expr.getQualifiedName().isPresent()) { // var
      final String varName = Names.getQualifiedName(expr.getQualifiedName().get().getParts());
      final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

      if (var.isPresent()) {
        return var.get().getType();
      }
      else {
        Log.warn("ExpressionCalculator cannot resolve the type of the variable: " + varName);
        // TODO handle it correctly
      }
    }
    else if (expr.getFunctionCall().isPresent()) { // function
      final String functionName = Names.getQualifiedName(expr.getFunctionCall().get().getQualifiedName().getParts());

      // TODO: use the helper to query function by parameters
      //final Object[] params = atom.getFunctionCall().getArgList().getArgs().toArray();
      final Optional<MethodSymbol> methodSymbol = scope.resolve(functionName,
          MethodSymbol.KIND);
      Preconditions.checkState(methodSymbol.isPresent(), "Cannot resolve the method: "
          + functionName);

      if (new TypeChecker().checkVoid(methodSymbol.get().getReturnType())) {
        final String errorMsg = "Function '%s' with returntype 'Void' cannot be used in expressions.";
        Log.error(ERROR_CODE + ":"+ String.format(errorMsg, functionName),
            expr.get_SourcePositionEnd());
      }

      return methodSymbol.get().getReturnType();
    }
    // TODO expr.leftParenthesesIsPresent must be handled
    else if (expr.getTerm().isPresent()) { // TODO it is a hack. the code with isUnaryPlus must work
      TypeSymbol type = computeType(expr.getTerm().get());
      if (isNumeric(type)) {
        return type;
      }
      else {
        final String errorMsg = "Cannot perform math operation on the not numeric type @<" + expr.get_SourcePositionStart() +
            ", " + expr.get_SourcePositionStart() + ">";

        throw new RuntimeException(errorMsg);
      }
    }
    else if (expr.isPlusOp()) {
      final TypeSymbol lhsType = computeType(expr.getLeft().get());
      final TypeSymbol rhsType = computeType(expr.getRight().get());

      // String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string
      if ((lhsType.equals(PredefinedTypes.getStringType()) ||
          rhsType.equals(PredefinedTypes.getStringType())) &&
          (!rhsType.equals(PredefinedTypes.getVoidType()) &&
          !lhsType.equals(PredefinedTypes.getVoidType()))) {
        return PredefinedTypes.getStringType();
      }
      if (isNumeric(lhsType) && isNumeric(rhsType)) {
        // in this case, neither of the sides is a String
        if ((lhsType.equals(PredefinedTypes.getRealType()) || lhsType.getType().equals(TypeSymbol.Type.UNIT)) ||
            (rhsType.equals(PredefinedTypes.getRealType()) || rhsType.getType().equals(TypeSymbol.Type.UNIT))) {
          return PredefinedTypes.getRealType();
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.equals(PredefinedTypes.getIntegerType()) ||
            rhsType.equals(PredefinedTypes.getIntegerType())) {
          return  PredefinedTypes.getIntegerType();
        }

        final String errorMsg = "Cannot determine the type of the operation with types: " + lhsType
             + ", " + rhsType + " at " + expr.get_SourcePositionStart() + ">";

        throw new RuntimeException(errorMsg);
      }
      // in this case, neither of the sides is a String
      if (lhsType.equals(PredefinedTypes.getRealType()) ||
          rhsType.equals(PredefinedTypes.getRealType())) {
        return PredefinedTypes.getRealType();
      }
      // e.g. both are integers, but check to be sure
      if (lhsType.equals(PredefinedTypes.getIntegerType()) ||
          rhsType.equals(PredefinedTypes.getIntegerType())) {
        return  PredefinedTypes.getIntegerType();
      }

      // TODO should be not possible
      final String errorMsg = "Cannot determine the type of the Expression-Node @<" + expr.get_SourcePositionStart() +
          ", " + expr.get_SourcePositionStart() + ">";

      throw new RuntimeException(errorMsg);
    }
    else if (expr.isMinusOp() || expr.isTimesOp() || expr.isDivOp()) {


      final TypeSymbol lhsType = computeType(expr.getLeft().get());
      final TypeSymbol rhsType = computeType(expr.getRight().get());

      if (isNumeric(lhsType) && isNumeric(rhsType)) {
        if (lhsType.equals(PredefinedTypes.getRealType()) ||
            rhsType.equals(PredefinedTypes.getRealType()) ||
            lhsType.getType().equals(TypeSymbol.Type.UNIT) ||
            rhsType.getType().equals(TypeSymbol.Type.UNIT)) {
          return PredefinedTypes.getRealType();
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.equals(PredefinedTypes.getIntegerType()) ||
            rhsType.equals(PredefinedTypes.getIntegerType())) {
          return  PredefinedTypes.getIntegerType();
        }

        final String errorMsg = "Cannot determine the type of the Expression-Node @<"
            + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();

        throw new RuntimeException(errorMsg);
      }
      else {
        final String errorMsg = "Cannot determine the type of the Expression-Node at"
            + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd() ;
        throw new RuntimeException(errorMsg);
      }

    }
    else if (expr.isPow()) {
      Preconditions.checkState(expr.getBase().isPresent());
      Preconditions.checkState(expr.getExponent().isPresent());
      final TypeSymbol baseType = computeType(expr.getBase().get());
      final TypeSymbol exponentType = computeType(expr.getExponent().get());

      if (!baseType.equals(PredefinedTypes.getStringType()) &&
          !exponentType.equals(PredefinedTypes.getStringType()) &&
          !baseType.equals(PredefinedTypes.getBooleanType()) &&
          !exponentType.equals(PredefinedTypes.getBooleanType()) &&
          !baseType.equals(PredefinedTypes.getVoidType()) &&
          !exponentType.equals(PredefinedTypes.getVoidType())) {
       return PredefinedTypes.getRealType();
      }
      else {

        SPLPrettyPrinter prettyPrinter = SPLPrettyPrinterFactory.createDefaultPrettyPrinter();
        expr.accept(prettyPrinter);
        final String errorMsg = "Cannot determine the type of the expression " + prettyPrinter.getResult() +" @<" + expr
            .get_SourcePositionStart() + ", " + expr.get_SourcePositionStart() + ">";
        throw new RuntimeException(errorMsg);
      }

    }
    else if (expr.isShiftLeft() ||
        expr.isShiftRight() ||
        expr.isModuloOp() ||
        expr.isBitAnd() ||
        expr.isBitOr() ||
        expr.isBitAnd()) {
      Preconditions.checkState(expr.getLeft().isPresent());
      Preconditions.checkState(expr.getRight().isPresent());

      final TypeSymbol lhsType = computeType(expr.getLeft().get());
      final TypeSymbol rhsType = computeType(expr.getRight().get());

      if (lhsType.equals(PredefinedTypes.getIntegerType()) &&
          rhsType.equals(PredefinedTypes.getIntegerType())) {
        return PredefinedTypes.getIntegerType();
      }
      else {
        final String errorMsg = "This operation expects both operands of the type integer @<" + expr.get_SourcePositionStart() +
            ", " + expr.get_SourcePositionStart() + ">";

        throw new RuntimeException(errorMsg);
      }
    }
    else if (expr.isLt() || expr.isLe() || expr.isEq() || expr.isNe() || expr.isNe2() || expr.isGe() || expr.isGt()) {
      final TypeSymbol lhsType = computeType(expr.getLeft().get());
      final TypeSymbol rhsType = computeType(expr.getRight().get());

      if (isNumeric(lhsType) && isNumeric(rhsType)) {
        return PredefinedTypes.getBooleanType();
      }
      else {
        final String errorMsg = "This operation expects both operands of a numeric type @<" + expr.get_SourcePositionStart() +
            ", " + expr.get_SourcePositionStart() + ">";

        throw new RuntimeException(errorMsg);
      }
    }

    if (expr.getExpr().isPresent()) {
      computeType(expr.getExpr().get());
    }
    else if (expr.isLogicalAnd() || expr.isLogicalOr()) {
      final TypeSymbol lhsType = computeType(expr.getLeft().get());
      final TypeSymbol rhsType = computeType(expr.getRight().get());
      if (lhsType.equals(PredefinedTypes.getBooleanType()) &&
          rhsType.equals(PredefinedTypes.getBooleanType())) {
        return PredefinedTypes.getBooleanType();
      }
      else {
        final String errorMsg = "Both operands of the logical expression must be boolean "
            + "' @" + expr.get_SourcePositionStart() ;

        throw new RuntimeException(errorMsg);
      }

    }

    SPLPrettyPrinter printer = SPLPrettyPrinterFactory.createDefaultPrettyPrinter();
    printer.print(expr);
    final String errorMsg = "Cannot determine the type of the Expression-Node '" + printer.getResult()
        + "' @" + expr.get_SourcePositionStart() ;

    throw new RuntimeException(errorMsg);
  }

  /**
   * Checks if the type is a numeric type, e.g. Integer or Real.
   */
  private boolean isNumeric(TypeSymbol type) {
    return type.equals(PredefinedTypes.getIntegerType()) ||
        type.equals(PredefinedTypes.getRealType()) ||
        type.getType().equals(TypeSymbol.Type.UNIT);

  }

}
