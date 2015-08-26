/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import com.google.common.base.Preconditions;
import de.monticore.cocos.CoCoLog;
import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl.prettyprinter.SPLPrettyPrinter;
import org.nest.spl.prettyprinter.SPLPrettyPrinterFactory;
import org.nest.spl._ast.ASTExpr;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

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

  private final PredefinedTypesFactory typesFactory;

  public ExpressionTypeCalculator(PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
  }

  public NESTMLTypeSymbol computeType(final ASTExpr expr) {
    Preconditions.checkNotNull(expr);
    checkArgument(expr.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = expr.getEnclosingScope().get();

    if (expr.leftParenthesesIsPresent()) {
      return computeType(expr.getExpr().get());
    }
    else if (expr.getNumericLiteral().isPresent()) { // number
      if (expr.getNumericLiteral().get() instanceof ASTDoubleLiteral) {
        return typesFactory.getRealType();
      }
      else if (expr.getNumericLiteral().get() instanceof ASTIntLiteral) {
        return typesFactory.getIntegerType();
      }

    }
    else if(expr.isInf()) {
      return typesFactory.getRealType();
    }
    else if (expr.getStringLiteral().isPresent()) { // string
      return typesFactory.getStringType();
    }
    else if (expr.getBooleanLiteral().isPresent()) { // boolean
      return typesFactory.getBooleanType();
    }
    else if (expr.getQualifiedName().isPresent()) { // var
      final String varName = Names.getQualifiedName(expr.getQualifiedName().get().getParts());
      final Optional<NESTMLVariableSymbol> var = scope.resolve(varName, NESTMLVariableSymbol.KIND);

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
      final Optional<NESTMLMethodSymbol> methodSymbol = scope.resolve(functionName,
          NESTMLMethodSymbol.KIND);
      Preconditions.checkState(methodSymbol.isPresent(), "Cannot resolve the method: "
          + functionName);

      if (new TypeChecker(typesFactory).checkVoid(methodSymbol.get().getReturnType())) {
        final String errorMsg = "Function '%s' with returntype 'Void' cannot be used in expressions.";
        CoCoLog.error(
            ERROR_CODE,
            String.format(errorMsg, functionName),
            expr.get_SourcePositionEnd());
      }

      return methodSymbol.get().getReturnType();
    }
    // TODO expr.leftParenthesesIsPresent must be handled
    else if (expr.getTerm().isPresent()) { // TODO it is a hack. the code with isUnaryPlus must work
      NESTMLTypeSymbol type = computeType(expr.getTerm().get());
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
      final NESTMLTypeSymbol lhsType = computeType(expr.getLeft().get());
      final NESTMLTypeSymbol rhsType = computeType(expr.getRight().get());

      // String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string
      if ((lhsType.equals(typesFactory.getStringType()) ||
          rhsType.equals(typesFactory.getStringType())) &&
          (!rhsType.equals(typesFactory.getVoidType()) &&
          !lhsType.equals(typesFactory.getVoidType()))) {
        return typesFactory.getStringType();
      }
      if (isNumeric(lhsType) && isNumeric(rhsType)) {
        // in this case, neither of the sides is a String
        if ((lhsType.equals(typesFactory.getRealType()) || lhsType.getType().equals(NESTMLTypeSymbol.Type.UNIT)) ||
            (rhsType.equals(typesFactory.getRealType()) || rhsType.getType().equals(NESTMLTypeSymbol.Type.UNIT))) {
          return typesFactory.getRealType();
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.equals(typesFactory.getIntegerType()) ||
            rhsType.equals(typesFactory.getIntegerType())) {
          return  typesFactory.getIntegerType();
        }

        final String errorMsg = "Cannot determine the type of the operation with types: " + lhsType
             + ", " + rhsType + " at " + expr.get_SourcePositionStart() + ">";

        throw new RuntimeException(errorMsg);
      }
      // in this case, neither of the sides is a String
      if (lhsType.equals(typesFactory.getRealType()) ||
          rhsType.equals(typesFactory.getRealType())) {
        return typesFactory.getRealType();
      }
      // e.g. both are integers, but check to be sure
      if (lhsType.equals(typesFactory.getIntegerType()) ||
          rhsType.equals(typesFactory.getIntegerType())) {
        return  typesFactory.getIntegerType();
      }

      // TODO should be not possible
      final String errorMsg = "Cannot determine the type of the Expression-Node @<" + expr.get_SourcePositionStart() +
          ", " + expr.get_SourcePositionStart() + ">";

      throw new RuntimeException(errorMsg);
    }
    else if (expr.isMinusOp() || expr.isTimesOp() || expr.isDivOp()) {


      final NESTMLTypeSymbol lhsType = computeType(expr.getLeft().get());
      final NESTMLTypeSymbol rhsType = computeType(expr.getRight().get());

      if (isNumeric(lhsType) && isNumeric(rhsType)) {
        if (lhsType.equals(typesFactory.getRealType()) ||
            rhsType.equals(typesFactory.getRealType()) ||
            lhsType.getType().equals(NESTMLTypeSymbol.Type.UNIT) ||
            rhsType.getType().equals(NESTMLTypeSymbol.Type.UNIT)) {
          return typesFactory.getRealType();
        }
        // e.g. both are integers, but check to be sure
        if (lhsType.equals(typesFactory.getIntegerType()) ||
            rhsType.equals(typesFactory.getIntegerType())) {
          return  typesFactory.getIntegerType();
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
      final NESTMLTypeSymbol baseType = computeType(expr.getBase().get());
      final NESTMLTypeSymbol exponentType = computeType(expr.getExponent().get());

      if (!baseType.equals(typesFactory.getStringType()) &&
          !exponentType.equals(typesFactory.getStringType()) &&
          !baseType.equals(typesFactory.getBooleanType()) &&
          !exponentType.equals(typesFactory.getBooleanType()) &&
          !baseType.equals(typesFactory.getVoidType()) &&
          !exponentType.equals(typesFactory.getVoidType())) {
       return typesFactory.getRealType();
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

      final NESTMLTypeSymbol lhsType = computeType(expr.getLeft().get());
      final NESTMLTypeSymbol rhsType = computeType(expr.getRight().get());

      if (lhsType.equals(typesFactory.getIntegerType()) &&
          rhsType.equals(typesFactory.getIntegerType())) {
        return typesFactory.getIntegerType();
      }
      else {
        final String errorMsg = "This operation expects both operands of the type integer @<" + expr.get_SourcePositionStart() +
            ", " + expr.get_SourcePositionStart() + ">";

        throw new RuntimeException(errorMsg);
      }
    }
    else if (expr.isLt() || expr.isLe() || expr.isEq() || expr.isNe() || expr.isNe2() || expr.isGe() || expr.isGt()) {
      final NESTMLTypeSymbol lhsType = computeType(expr.getLeft().get());
      final NESTMLTypeSymbol rhsType = computeType(expr.getRight().get());

      if (isNumeric(lhsType) && isNumeric(rhsType)) {
        return typesFactory.getBooleanType();
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
      final NESTMLTypeSymbol lhsType = computeType(expr.getLeft().get());
      final NESTMLTypeSymbol rhsType = computeType(expr.getRight().get());
      if (lhsType.equals(typesFactory.getBooleanType()) &&
          rhsType.equals(typesFactory.getBooleanType())) {
        return typesFactory.getBooleanType();
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
  private boolean isNumeric(NESTMLTypeSymbol type) {
    return type.equals(typesFactory.getIntegerType()) ||
        type.equals(typesFactory.getRealType()) ||
        type.getType().equals(NESTMLTypeSymbol.Type.UNIT);

  }

}
