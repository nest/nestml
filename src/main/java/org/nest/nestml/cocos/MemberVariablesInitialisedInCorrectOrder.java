/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.Names;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._ast.ASTVariable;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Variables in a block must be defined before used. Only variables from parameters are allowed
 * to be used before definition
 *
 * @author ippen, plotnikov
 */
public class MemberVariablesInitialisedInCorrectOrder implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_MEMBER_VARIABLES_INITIALISED_IN_CORRECT_ORDER";

  /**
   * AliasDecl = ([hide:"-"])? ([alias:"alias"])? Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
   * Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
   *
   */
  public void check(final ASTAliasDecl alias) {
    final Optional<? extends Scope> enclosingScope = alias.getEnclosingScope();
    checkState(enclosingScope.isPresent(),
        "There is no scope assigned to the AST node: " + alias);
    ASTDeclaration declaration = alias.getDeclaration();

    if (declaration.getExpr().isPresent() && declaration.getVars().size() > 0) {
      final String lhsVariableName = declaration.getVars().get(0); // has at least one declaration

      final Optional<VariableSymbol> lhsSymbol = enclosingScope.get().resolve(
          lhsVariableName,
          VariableSymbol.KIND); // TODO use cached version

      checkState(lhsSymbol.isPresent(), "Variable '" + lhsVariableName + "' is not defined");

      final List<ASTVariable> variablesNames
          = ASTNodes.getSuccessors(declaration.getExpr().get(), ASTVariable.class);

      if (checkVariables(enclosingScope.get(), lhsSymbol.get(), variablesNames))
        return;

      for (ASTExpr aliasExpression:alias.getInvariants()) {
        final List<ASTVariable> namesInInvariant
            = ASTNodes.getSuccessors(aliasExpression, ASTVariable.class);

        if (checkVariables(enclosingScope.get(), lhsSymbol.get(), namesInInvariant))
          return;

      }

    }

  }

  protected boolean checkVariables(
      final Scope enclosingScope,
      final VariableSymbol lhsSymbol,
      final List<ASTVariable> variablesNames) {
    for (final ASTVariable astVariable : variablesNames) {
      final String rhsVariableName = astVariable.toString();
      final Optional<VariableSymbol> rhsSymbol = enclosingScope.resolve(
          rhsVariableName,
          VariableSymbol.KIND);

      if (!rhsSymbol.isPresent()) { // actually redudant and it is should be checked through another CoCo
        final String msg = astVariable.get_SourcePositionStart() + ": Variable '" +
            rhsVariableName + "' is undefined.";
        Log.warn(msg);
        return true;
      }
      else  { //
        // not local, e.g. a variable in one of the blocks: state, parameter, or internal
        // both of same decl type
        checkIfDefinedInCorrectOrder(lhsSymbol, rhsSymbol.get());

      }

    }
    return false;
  }

  protected void checkIfDefinedInCorrectOrder(
      final VariableSymbol lhsSymbol,
      final VariableSymbol rhsSymbol) {
    if (rhsSymbol.getDeclaringType().getName()
        .equals(lhsSymbol.getDeclaringType().getName())) {
      // same var - block? => used must be in
      // previous line
      if (rhsSymbol.getBlockType() == lhsSymbol.getBlockType()) {
        // same block not parameter block
        if (rhsSymbol.getSourcePosition().getLine() >
            lhsSymbol.getSourcePosition().getLine()) {
          final String msg = "Variable '"
              + rhsSymbol.getName()
              + "' must be declared before it can be used in declaration of '"
              + lhsSymbol.getName() + "'.";
          error(ERROR_CODE + ": " + msg, rhsSymbol.getSourcePosition());

        }
      }
      if (rhsSymbol.getBlockType() != lhsSymbol.getBlockType() &&
          rhsSymbol.getBlockType() != VariableSymbol.BlockType.PARAMETER) {
        final String msg = "Variable '"
            + rhsSymbol.getName()
            + "' must be declared in the parameter block to be used at this place. '"
            + lhsSymbol.getName() + "'.";
       error(ERROR_CODE + ":" + msg, rhsSymbol.getSourcePosition());
      }

    }

  }



}
