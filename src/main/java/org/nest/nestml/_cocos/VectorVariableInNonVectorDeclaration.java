/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTVariable;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.monticore.utils.ASTNodes.getSuccessors;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that an alias is not used in the declaring expression of an non alias declaration
 * n  integer
 * alias three integer[n] = 3
 * threePlusFour integer = three + 4 <- error: threePlusFour is not a vector
 * @author plotnikov, ippen
 */
public class VectorVariableInNonVectorDeclaration implements NESTMLASTAliasDeclCoCo {

  @Override
  public void check(ASTAliasDecl astAliasDecl) {
    checkState(astAliasDecl.getEnclosingScope().isPresent(), "Run symbol table creator");
    final Scope scope = astAliasDecl.getEnclosingScope().get();
    final ASTDeclaration decl = astAliasDecl.getDeclaration();

    if (decl.getExpr().isPresent()) {
      final List<ASTVariable> variables = getSuccessors(decl.getExpr().get(), ASTVariable.class);

      for (final ASTVariable variable : variables) {
        final VariableSymbol stentry = VariableSymbol.resolve(variable.toString(), scope);

        // used is set here
        if (stentry.isVector() && !astAliasDecl.getDeclaration().getSizeParameter().isPresent()) {
          final String msg = NestmlErrorStrings.message(this, stentry.getName(), decl.get_SourcePositionStart());
          error(msg, decl.get_SourcePositionStart());
        }

      }

    }

  }

}
