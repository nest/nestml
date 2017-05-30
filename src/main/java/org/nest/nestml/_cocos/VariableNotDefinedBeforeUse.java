/*
 * VariableNotDefinedBeforeUse.java
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

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;
import org.nest.nestml._symboltable.predefined.PredefinedVariables;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.Collection;
import java.util.List;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that a variable used in an statement is defined before.
 *
 * @author ippen, plotnikov
 */
public class VariableNotDefinedBeforeUse implements
    NESTMLASTAssignmentCoCo,
    NESTMLASTDeclarationCoCo,
    NESTMLASTFOR_StmtCoCo,
    NESTMLASTWHILE_StmtCoCo,
    NESTMLASTFunctionCallCoCo {

  @Override
  public void check(final ASTFOR_Stmt forstmt) {
    String fullName = forstmt.getVar();
    check(fullName, forstmt);
    final List<ASTVariable> variables = ASTNodes.getSuccessors(forstmt.getFrom(), ASTVariable.class);
    variables.addAll(ASTNodes.getSuccessors(forstmt.getTo(), ASTVariable.class));
    variables.forEach(variable -> check(variable.toString(), forstmt));
  }

  @Override
  public void check(final ASTAssignment assignment) {
      check(assignment.getLhsVarialbe().toString(), assignment);
  }

  @Override
  public void check(final ASTDeclaration decl) {
    checkArgument(decl.getEnclosingScope().isPresent(), "Run symboltable creator.");
    final Scope scope = decl.getEnclosingScope().get();

    if (decl.getExpr().isPresent()) {

      final List<String> varsOfCurrentDecl = Lists.newArrayList(decl.getVars());
      final List<ASTVariable> variablesNamesRHS = ASTNodes.getSuccessors(decl.getExpr().get(), ASTVariable.class);
      // check if it is variable block or dynamics- or user-defined function. if yes, skip the check. It will be
      // checked through MemberVariablesInitialisedInCorrectOrder coco
      final Collection<VariableSymbol> declarationSymbols = scope.resolveMany(varsOfCurrentDecl.get(0), VariableSymbol.KIND);

      if(declarationSymbols.size()>1){ //named after an SI-Unit? Throw away predefined result.
        declarationSymbols.removeIf(VariableSymbol::isPredefined);
        checkState(declarationSymbols.size() == 1);
      }
      VariableSymbol declarationSymbol = declarationSymbols.iterator().next();

      if (!declarationSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
        return;
      }
      // check, if variable of the left side is used in the right side, e.g. in decl-vars
      for (final ASTVariable variable: variablesNamesRHS) {
        final String varRHS = variable.toString();
        final VariableSymbol variableSymbol =VariableSymbol.resolve(varRHS, scope);
        if (PredefinedVariables.gerVariables().contains(variableSymbol)) {
          continue;
        }
        // e.g. x real = 2 * x
        if (varsOfCurrentDecl.contains(varRHS)) {
          final String logMsg = SplErrorStrings.messageOwnAssignment(this, varRHS);
          error(logMsg, decl.get_SourcePositionStart());
        }
        else if (variable.get_SourcePositionStart().compareTo(variableSymbol.getAstNode().get().get_SourcePositionStart()) < 0) {
          // y real = 5 * x
          // x integer = 1
          final String logMsg = SplErrorStrings.messageDefinedBeforeUse(this, variable.toString(), decl.get_SourcePositionStart());
          error(logMsg, decl.get_SourcePositionStart());
        }

      }

    }

  }

  protected void check(final String varName, final ASTNode node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = node.getEnclosingScope().get();

    VariableSymbol variableDefinition = VariableSymbol.resolve(varName, scope);

    // exists
    if (variableDefinition.getBlockType().equals(VariableSymbol.BlockType.LOCAL) &&
        node.get_SourcePositionStart().compareTo(variableDefinition.getSourcePosition()) < 0) {
      final String msg = SplErrorStrings.messageDefinedBeforeUse(
          this,
          varName,
          variableDefinition.getSourcePosition());
      Log.error(msg, node.get_SourcePositionEnd());
    }

  }

  @Override
  public void check(final ASTWHILE_Stmt astWhileStmt) {
    final List<ASTVariable> variables = ASTNodes.getSuccessors(astWhileStmt.getExpr(), ASTVariable.class);
    variables.forEach(variable -> check(variable.toString(), astWhileStmt));
  }

  @Override
  public void check(ASTFunctionCall astFunctionCall) {
    final List<ASTVariable> variables = Lists.newArrayList();
    astFunctionCall.getArgs().forEach(argExpr -> variables.addAll(ASTNodes.getSuccessors(argExpr, ASTVariable.class)));
    variables.forEach(variable -> check(variable.toString(), astFunctionCall));
  }

}
