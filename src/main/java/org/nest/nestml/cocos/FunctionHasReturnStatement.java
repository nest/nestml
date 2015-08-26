package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import de.monticore.ast.ASTNode;
import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.spl._ast.*;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Checks that a function with a return value has a returning block of code. If
 * the return statements of its block have the correct type is checked with
 * another coco.
 *
 * @author Tammo Ippen
 */
public class FunctionHasReturnStatement implements NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "NESTML_FUNCTION_HAS_RETURN_STATEMENT";

  private final PredefinedTypesFactory predefinedTypesFactory;

  public FunctionHasReturnStatement(PredefinedTypesFactory predefinedTypesFactory) {
    this.predefinedTypesFactory = predefinedTypesFactory;
  }

  @Override
  public void check(final ASTFunction fun) {
    checkArgument(fun.getEnclosingScope().isPresent(), "No scope is assigned. Run symbol table creator.");
    final Scope scope = fun.getEnclosingScope().get();

    if (fun.getReturnType().isPresent()) {
      // check if void type is stated
      final String typeName = Names.getQualifiedName(fun.getReturnType().get().getParts());
      Optional<NESTMLTypeSymbol> rType = scope.resolve(typeName, NESTMLTypeSymbol.KIND);
      Preconditions.checkState(rType.isPresent(), "Cannot resolve the type: " + typeName);

      // TODO fix the problem with the FQN of the predefined types
      if (rType.get().getFullName().equals(predefinedTypesFactory.getVoidType().getName())) {
        return;
      }

      // non void return type
      // if block not returning:
      if (isReturnBlock(fun.getBlock()) == null) {
        final String msg = "Function '" + fun.getName()
                + "' must return a result of type '"
                + fun.getReturnType().get().toString();
        CoCoLog.error(
            ERROR_CODE,
            msg,
            fun.get_SourcePositionStart());
      }

    }

  }

  protected ASTNode isReturnBlock(final ASTBlock block) {

    // Block = Stmt*
    for (ASTStmt stmt : block.getStmts()) {

      // Stmt = Simple_Stmt | Compound_Stmt;
      if (stmt.getSimple_Stmt().isPresent() && stmt.getSimple_Stmt().get().getSmall_Stmts() != null) {
        // Simple_Stmt = Small_Stmt (options {greedy=true;}:";" Small_Stmt)* (";")?;
        for (ASTSmall_Stmt small : stmt.getSimple_Stmt().get().getSmall_Stmts()) {
          // Small_Stmt = (DottedName "=") => Assignment |
          // FunctionCall | Declaration | ReturnStmt;
          if (small.getReturnStmt().isPresent()) {
            // return found!
            return small.getReturnStmt().get();
          }
        }
      } else if (stmt.getCompound_Stmt().isPresent()) {
        ASTNode r = isReturnCompound(stmt.getCompound_Stmt().get());
        if (r != null) {
          return r;
        }
      }
    }
    return null;
  }

  private ASTNode isReturnCompound(ASTCompound_Stmt compound) {
    // Compound_Stmt = IF_Stmt | FOR_Stmt | WHILE_Stmt;
    if (compound.getIF_Stmt().isPresent()) {
      return isIFReturn(compound.getIF_Stmt().get());
    } else if (compound.getFOR_Stmt().isPresent()
            && isReturnBlock(compound.getFOR_Stmt().get().getBlock()) != null) {
      return compound.getFOR_Stmt().get();
    } else if (compound.getWHILE_Stmt().isPresent()
            && isReturnBlock(compound.getWHILE_Stmt().get().getBlock()) != null) {
      return compound.getWHILE_Stmt().get();
    }

    return null;
  }

  private ASTNode isIFReturn(ASTIF_Stmt ifStmt) {
    // 1) need an else block
    if (ifStmt.getELSE_Clause() == null) {
      return null;
    }

    // 2) all if/elif/else blocks need to be returning
    boolean allReturn = true;
    allReturn = allReturn && isReturnBlock(ifStmt.getIF_Clause().getBlock()) != null;
    if (ifStmt.getELSE_Clause().isPresent()) {
      allReturn = allReturn
              && isReturnBlock(ifStmt.getELSE_Clause().get().getBlock()) != null;
    } else {
      return null;
    }

    for (ASTELIF_Clause elif : ifStmt.getELIF_Clauses()) {
      allReturn = allReturn && isReturnBlock(elif.getBlock()) != null;
    }
    return allReturn ? ifStmt : null;
  }

}
