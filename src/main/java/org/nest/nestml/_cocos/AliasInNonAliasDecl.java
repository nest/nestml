/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.commons._ast.ASTVariable;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.monticore.utils.ASTNodes.getSuccessors;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that an alias is not used in the declaring expression of an non alias declaration
 * alias a real = s + 1
 * b real = a <-- is an error
 * @author plotnikov, ippen
 */
public class AliasInNonAliasDecl implements NESTMLASTNeuronCoCo, NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_IN_NON_ALIAS_DECL";

  @Override
  public void check(final ASTComponent astComponent) {
    final ASTBody astBodyDecorator = astComponent.getBody();
    final Optional<NeuronSymbol> componentSymbol
        = (Optional<NeuronSymbol>) astComponent.getSymbol();
    checkState(componentSymbol.isPresent());
    checkAllAliasesInNeuron(astBodyDecorator, componentSymbol.get());
  }

  @Override
  public void check(final ASTNeuron astNeuron) {
    final ASTBody astBodyDecorator = (astNeuron.getBody());
    final Optional<NeuronSymbol> neuronSymbol
        = (Optional<NeuronSymbol>) astNeuron.getSymbol();
    checkState(neuronSymbol.isPresent());
    checkAllAliasesInNeuron(astBodyDecorator, neuronSymbol.get());
  }

  public void checkAllAliasesInNeuron(
      final ASTBody astBodyDecorator,
      final NeuronSymbol neuronSymbol) {
    astBodyDecorator.getInternalDeclarations().forEach(astFunction -> checkAlias(astFunction, neuronSymbol));
    astBodyDecorator.getStateDeclarations().forEach(astFunction -> checkAlias(astFunction, neuronSymbol));
    astBodyDecorator.getParameterDeclarations().forEach(astFunction -> checkAlias(astFunction, neuronSymbol));
  }

  public void checkAlias(final ASTAliasDecl alias, final NeuronSymbol neuronSymbol) {
    if (!alias.isAlias() && alias.getDeclaration().exprIsPresent()) {
      final ASTDeclaration decl = alias.getDeclaration();
      Optional<VariableSymbol> used;

      final List<ASTVariable> variables = getSuccessors(decl.getExpr().get(), ASTVariable.class);
      // TODO Review the "reflection code"
      for (final ASTVariable atomFqn : variables) {
        final String fullName = atomFqn.toString();

        final Optional<VariableSymbol> stentry = neuronSymbol.getVariableByName(fullName);
        if (stentry.isPresent()) {
          used = stentry;
        }
        else {
          continue;
        }

        if (!used.isPresent()) { // should not happen, but makes compiler
          continue;
        }

        // used is set here
        if (used.get().isAlias() && used.get().isVector()) {
          CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
          final String msg = errorStrings.getErrorMsg(this,used.get().getName());
          error(msg, decl.get_SourcePositionStart());
        }

      }

    }

  }

}
