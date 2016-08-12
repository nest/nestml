package org.nest.nestml._cocos;

import static com.google.common.base.Preconditions.checkArgument;
import java.util.Optional;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._ast.ASTFunction;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTReturnStmt;
import org.nest.spl._ast.ASTSmall_Stmt;
import org.nest.spl._ast.ASTStmt;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

/**
 * @author ptraeder
 */
public class LiteralsHaveTypes implements
    SPLASTAssignmentCoCo,
    CommonsASTFunctionCallCoCo,
    SPLASTDeclarationCoCo,
    NESTMLASTFunctionCoCo{
  public static final String ERROR_CODE = "NESTML_LITERALS_MUST_HAVE_TYPES";

  @Override
  /**
   * For Variable assignments, check that a rhs literal carries unit information
   *
   * Valid: Ampere = 8 A
   * Invalid: Ampere = 8
   */
  public void check(ASTAssignment node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
      checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
      Optional<VariableSymbol> var = enclosingScope.get().resolve(node.getLhsVarialbe().getName().toString(),VariableSymbol.KIND);
      if(var.isPresent()) {
        if (var.get().getType().getType() == TypeSymbol.Type.UNIT) {
          if (node.getExpr().nESTMLNumericLiteralIsPresent()) {
            if (!node.getExpr().getNESTMLNumericLiteral().get().getType().isPresent()) {

              CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
              final String msg = errorStrings.getErrorMsgAssignment(this);
              Log.warn(msg, node.get_SourcePositionStart());
            }
          }
        }
      }

  }

  @Override
  /**
   * For Variable declarations, check that a initializing literal carries unit information
   *
   * Valid: Ampere A = 8 A
   * Invalid Ampere A = 8
   */
  public void check(ASTDeclaration node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resovle with the first var name from the declaration
    Optional<VariableSymbol> var = enclosingScope.get().resolve(node.getVars().get(0),VariableSymbol.KIND);
    if(var.isPresent()) {
      if (var.get().getType().getType() == TypeSymbol.Type.UNIT) {
        if (node.getExpr().isPresent()) {
          if(node.getExpr().get().getNESTMLNumericLiteral().isPresent())
          if (!node.getExpr().get().getNESTMLNumericLiteral().get().getType().isPresent()) {
            CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
            final String msg = errorStrings.getErrorMsgAssignment(this);
            Log.warn(msg, node.get_SourcePositionStart());
          }
        }
      }
    }
  }

  @Override
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

  public void check(ASTFunctionCall node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resolve method
    Optional<MethodSymbol> methodSymbol  = enclosingScope.get().resolve(node.getCalleeName(),MethodSymbol.KIND);
    if(methodSymbol.isPresent()) {
      for( int it = 0; it<methodSymbol.get().getParameterTypes().size();it++){
        TypeSymbol typeSymbol = methodSymbol.get().getParameterTypes().get(it);
        ASTExpr parameterExpr = node.getArgs().get(it);
        if(typeSymbol.getType() == TypeSymbol.Type.UNIT){
          if(parameterExpr.nESTMLNumericLiteralIsPresent()){
            if(!parameterExpr.getNESTMLNumericLiteral().get().typeIsPresent()){
              CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
              final String msg = errorStrings.getErrorMsgCall(this);
              Log.warn(msg, node.get_SourcePositionStart());
            }
          }
        }
      }
    }
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
  @Override public void check(ASTFunction node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resolve method
    Optional<MethodSymbol> methodSymbol  = enclosingScope.get().resolve(node.getName(),MethodSymbol.KIND);
    if(methodSymbol.isPresent()) {
      if (methodSymbol.get().getReturnType().getType() == TypeSymbol.Type.UNIT) {

        //if return Type is unit, iterate over return statements
        for (ASTStmt statement : node.getBlock().getStmts()) {
          if (statement.simple_StmtIsPresent()) {
            for (ASTSmall_Stmt small_stmt : statement.getSimple_Stmt().get().getSmall_Stmts()) {
              if (small_stmt.returnStmtIsPresent()) {
                //found a return statement inside the function
                ASTReturnStmt returnStmt = small_stmt.getReturnStmt().get();
                if(returnStmt.exprIsPresent()){
                  if(returnStmt.getExpr().get().nESTMLNumericLiteralIsPresent()){
                    if(!returnStmt.getExpr().get().getNESTMLNumericLiteral().get().typeIsPresent()){
                      CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
                      final String msg = errorStrings.getErrorMsgReturn(this);
                      Log.warn(msg, node.get_SourcePositionStart());
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
