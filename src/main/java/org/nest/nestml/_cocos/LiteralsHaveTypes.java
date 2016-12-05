/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._cocos.CommonsASTExprCoCo;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._ast.ASTFunction;
import org.nest.spl._ast.*;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 *
 *
 * @author ptraeder
 */
public class LiteralsHaveTypes implements
    SPLASTAssignmentCoCo,
    CommonsASTFunctionCallCoCo,
    SPLASTDeclarationCoCo,
    NESTMLASTFunctionCoCo,
    CommonsASTExprCoCo{
  public static final String ERROR_CODE = "NESTML_LITERALS_MUST_HAVE_TYPES";

  /**
   * For Variable assignments, check that a rhs expression carries unit information
   *
   * Valid: Ampere = 8 A
   * Invalid: Ampere = 8
   */
  @Override
  public void check(ASTAssignment node) {
    /*final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    Optional<VariableSymbol> var = enclosingScope.get().resolve(node.getLhsVarialbe().getName().toString(),VariableSymbol.KIND);
    if(var.isPresent()) {
      if (var.get().getType().getType() == TypeSymbol.Type.UNIT) {
        final Either<TypeSymbol,String> exprType;
        exprType = node.getExpr().getType();

        if (exprType.isValue() &&
            !exprType.getValue().getType().equals(TypeSymbol.Type.UNIT)){
          NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
          final String msg = errorStrings.getErrorMsgAssignment(this);
          Log.warn(msg + " at " + node.get_SourcePositionStart(), node.get_SourcePositionStart());
        }

      }

    }*/

  }

  /**
   * For Variable declarations, check that a initializing literal carries unit information
   *
   * Valid: Ampere A = 8 A
   * Invalid Ampere A = 8
   */
  @Override
  public void check(ASTDeclaration node) {
   /* final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resovle with the first var name from the declaration
    Optional<VariableSymbol> var = enclosingScope.get().resolve(node.getVars().get(0),VariableSymbol.KIND);
    if(var.isPresent()) {
      if (var.get().getType().getType() == TypeSymbol.Type.UNIT) {
        if (node.getExpr().isPresent()) {
          Either<TypeSymbol,String> exprType;
          exprType = node.getExpr().get().getType();

          if (exprType.isValue() &&
              // !exprType.getValue().equals(var.get().getType())) {
              !exprType.getValue().getType().equals(TypeSymbol.Type.UNIT)){
            NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
            final String msg = errorStrings.getErrorMsgAssignment(this);
            Log.warn(msg + " at " + node.get_SourcePositionStart() , node.get_SourcePositionStart());
          }

        }

      }

    }*/

  }

  /**
   * For Function calls, check that a literal parameter carries
   * unit information if the parameter is of unit type
   *
   * function foo(ohm Ohm,amp A) V:
   *          ...
   *  end
   *
   *  Valid:
   *        foo(2 Ohm,4 A)
   *  Invalid:
   *        foo(2,4)
   */

  @Override
  public void check(ASTFunctionCall node) {
 /*   final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resolve method
    Optional<MethodSymbol> methodSymbol  = enclosingScope.get().resolve(node.getCalleeName(),MethodSymbol.KIND);
    if(methodSymbol.isPresent()) {
      for( int it = 0; it<methodSymbol.get().getParameterTypes().size();it++){
        TypeSymbol parameterType = methodSymbol.get().getParameterTypes().get(it);
        ASTExpr parameterExpr = node.getArgs().get(it);
        if(parameterType.getType() == TypeSymbol.Type.UNIT){
          Either<TypeSymbol,String> exprType;
          exprType = parameterExpr.getType();

          if (exprType.isValue() &&
              //!exprType.getValue().equals(parameterType)) {
              !exprType.getValue().getType().equals(TypeSymbol.Type.UNIT)) {
            NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
            final String msg = errorStrings.getErrorMsgCall(this);
            Log.warn(msg + " at " + node.get_SourcePositionStart(), node.get_SourcePositionStart());
          }

        }

      }

    }
 */
  }

  /**
   * For Function declarations, check if the function returns a Unit type.
   * If it does, assert for every return statement that returns a literal
   * carries unit type information
   *
   * Valid:
   *        function foo(ohm Ohm,amp A) V:
   *          ...
   *          return 8V
   *        end
   *
   *  Invalid:
   *        function foo(ohm Ohm,amp A) V:
   *          ...
   *          return 8
   *        end
   */
  @Override
  public void check(ASTFunction node) {
  /*  final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resolve method
    Optional<MethodSymbol> methodSymbol  = enclosingScope.get().resolve(node.getName(),MethodSymbol.KIND);
    if(methodSymbol.isPresent()) {
      if (methodSymbol.get().getReturnType().getType() == TypeSymbol.Type.UNIT) {
        //TypeSymbol methodReturnType = methodSymbol.get().getReturnType();
        //if return Type is unit, iterate over return statements
        for (ASTStmt statement : node.getBlock().getStmts()) {
          if (statement.small_StmtIsPresent()) {
            ASTSmall_Stmt small_stmt = statement.getSmall_Stmt().get();
              if (small_stmt.returnStmtIsPresent()) {
                //found a return statement inside the function
                ASTReturnStmt returnStmt = small_stmt.getReturnStmt().get();
                if(returnStmt.exprIsPresent()){
                  Either<TypeSymbol,String> returnType;
                  returnType = returnStmt.getExpr().get().getType();

                  if (returnType.isValue() &&
                     // !exprType.getValue().equals(returnType)) {
                      !returnType.getValue().getType().equals(TypeSymbol.Type.UNIT)) {
                    NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
                    final String msg = errorStrings.getErrorMsgReturn(this);
                    Log.warn(msg, node.get_SourcePositionStart());
                  }

                }

              }

          }

        }

      }

    }*/

  }

/*  @Override public void check(ASTIF_Clause node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    ASTExpr expr = node.getExpr();
    checkConditionalExpression(expr);
  }

  @Override public void check(ASTELIF_Clause node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    ASTExpr expr = node.getExpr();
    checkConditionalExpression(expr);
  }

  void checkConditionalExpression(ASTExpr expr){
    if(expr.isLogicalAnd() || expr.isLogicalOr()){
      checkConditionalExpression(expr.getLeft().get());
      checkConditionalExpression(expr.getRight().get());
    }
    if(expr.nESTMLNumericLiteralIsPresent()){
      if(!expr.getNESTMLNumericLiteral().get().getType().isPresent()){
        SplErrorStrings errorStrings = SplErrorStrings.getInstance();
        final String msg = errorStrings.getErrorMsgConditional(this);
        Log.warn(msg, expr.get_SourcePositionStart());
      }
    }
  }*/

  @Override
  public void check(ASTExpr node) {
/*    if(node.isLt() || node.isLe() || node.isEq() || node.isNe() ||
        node.isNe2() || node.isGe() || node.isGt()){
      final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
      checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
      final Either<TypeSymbol,String> leftType,rightType;
      leftType = node.getLeft().get().getType();
      rightType = node.getRight().get().getType();

      if (leftType.isValue() && rightType.isValue()){ // Types are Recognized
        if(leftType.getValue().getType() == TypeSymbol.Type.UNIT ||
            rightType.getValue().getType() == TypeSymbol.Type.UNIT) {// at least one of the involved types is UNIT
          if(!leftType.getValue().getType().equals(TypeSymbol.Type.UNIT)||
              !rightType.getValue().getType().equals(TypeSymbol.Type.UNIT)){ //BOTH are NOT units
            NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
            final String msg = errorStrings.getErrorMsgConditional(this) + ": " + node.get_SourcePositionStart();
            Log.warn(msg, node.get_SourcePositionStart());
          }

        }

      }

    }*/

  }

}
