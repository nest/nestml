/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import com.google.common.base.Preconditions;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.spl._ast.*;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.spl.symboltable.typechecking.TypeChecker.deserializeUnitIfNotPrimitive;
import static org.nest.utils.AstUtils.computeTypeName;

/**
 * Checks that a function with a return value has a returning block of code. If
 * the return statements of its block have the correct type is checked with
 * another coco.
 *
 * @author ippen, plotnikov
 */
public class MissingReturnStatementInFunction implements NESTMLASTFunctionCoCo {

  @Override
  public void check(final ASTFunction fun) {
    checkArgument(fun.getEnclosingScope().isPresent(), "No scope is assigned. Run symbol table creator.");
    final Scope scope = fun.getEnclosingScope().get();

    if (fun.getReturnType().isPresent()) {
      // check if void type is stated
      final String typeName = computeTypeName(fun.getReturnType().get());
      Optional<TypeSymbol> rType = scope.resolve(typeName, TypeSymbol.KIND);
      Preconditions.checkState(rType.isPresent(), "Cannot resolve the type: " + typeName);

      // TODO fix the problem with the FQN of the predefined types
      if (rType.get().getFullName().equals(PredefinedTypes.getVoidType().getName())) {
        return;
      }

      // non void return type
      // if block not returning:
      if (isReturnBlock(fun.getBlock()) == null) {
        NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
        final String msg = NestmlErrorStrings.getErrorMsg(this, fun.getName(), deserializeUnitIfNotPrimitive(computeTypeName(fun.getReturnType().get())));

        Log.error(msg, fun.get_SourcePositionStart());
      }

    }

  }

  protected ASTNode isReturnBlock(final ASTBlock block) {

    // Block = Stmt*
    for (ASTStmt stmt : block.getStmts()) {

      // Stmt = Simple_Stmt | Compound_Stmt;
      if (stmt.small_StmtIsPresent()) {
        final ASTSmall_Stmt small = stmt.getSmall_Stmt().get();
        if (small.getReturnStmt().isPresent()) {
          // return found!
          return small.getReturnStmt().get();
        }
      }
      else if (stmt.getCompound_Stmt().isPresent()) {
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
    }
    else if (compound.getFOR_Stmt().isPresent()
             && isReturnBlock(compound.getFOR_Stmt().get().getBlock()) != null) {
      return compound.getFOR_Stmt().get();
    }
    else if (compound.getWHILE_Stmt().isPresent()
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
    }
    else {
      return null;
    }

    for (ASTELIF_Clause elif : ifStmt.getELIF_Clauses()) {
      allReturn = allReturn && isReturnBlock(elif.getBlock()) != null;
    }
    return allReturn ? ifStmt : null;
  }

}
