/*
 * CodeAfterReturn.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import de.se_rwth.commons.SourcePosition;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;

/**
 * Checks that that there is no statements after the return statement.
 * TODO refactor, code is unmaintable
 * @author ippen, plotnikov
 */
public class CodeAfterReturn implements NESTMLASTBlockCoCo {


  @Override
  public void check(ASTBlock block) {
    // && TODO  isToplevelBlock(block)
    if (!block.getStmts().isEmpty()) {
      isReturnBlock(block);
    }

  }

  private ASTNode isReturnBlock(ASTBlock block) {
    ASTNode r = null;

    // Block = Stmt*
    for (ASTStmt stmt : block.getStmts()) {
      // error, if already found return and have a next stmt
      if (r != null) {
        if (r instanceof ASTReturnStmt) {
          addReport(
                  "Code after the a return statement is not reachable!",
                  r.get_SourcePositionStart());
        } else if (r instanceof ASTIF_Stmt) {
          addReport(
                  "Code after the a returning if-statement is not reachable!",
                  r.get_SourcePositionStart());
        } else if (r instanceof ASTFOR_Stmt) {
          addReport(
                  "Code after the a returning for-statement is not reachable!",
                  r.get_SourcePositionStart());
        } else if (r instanceof ASTWHILE_Stmt) {
          addReport(
                  "Code after the a returning while-statement is not reachable!",
                  r.get_SourcePositionStart());
        }

        return r;
      }
      // Stmt = Simple_Stmt | Compound_Stmt;
      if (stmt.getSmall_Stmt().isPresent()) {
        final ASTSmall_Stmt small = stmt.getSmall_Stmt().get();
        // error, if return found in line and new small found
        if (r != null) {
          addReport("Code after a return statement is not reachable!", r.get_SourcePositionStart());
          return r;
        }
        // Small_Stmt = (DottedName "=") => Assignment |
        // FunctionCall | Declaration | ReturnStmt;
        if (small.getReturnStmt().isPresent()) {
          // return found!
          r = small.getReturnStmt().get();
        }
      }
      else if (stmt.getCompound_Stmt().isPresent()) {
        r = isReturnCompound(stmt.getCompound_Stmt().get());
      }
    }
    return r;
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
    if (!ifStmt.getELSE_Clause().isPresent()) {
      return null;
    }

    // 2) all if/elif/else blocks need to be returning
    boolean allReturn = true;
    allReturn = allReturn && isReturnBlock(ifStmt.getIF_Clause().getBlock()) != null;
    // TODO ifStmt.getELSE_Clause() is an optional, handle it correctly
    allReturn = allReturn
            && isReturnBlock(ifStmt.getELSE_Clause().get().getBlock()) != null;
    for (ASTELIF_Clause elif : ifStmt.getELIF_Clauses()) {
      allReturn = allReturn && isReturnBlock(elif.getBlock()) != null;
    }
    return allReturn ? ifStmt : null;
  }

  private void addReport(final String errorMessage, final SourcePosition sourcePositionStart) {
    Log.error(SplErrorStrings.message(this, errorMessage), sourcePositionStart);
  }

}
