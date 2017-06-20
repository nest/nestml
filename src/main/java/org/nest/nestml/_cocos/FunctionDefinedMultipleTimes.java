/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;

import java.util.Collection;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Methods must be unique. If there are two methods with same name, than they must have
 * different argument types.
 * @author ippen, plotnikov
 */
public class FunctionDefinedMultipleTimes implements NESTMLASTNeuronCoCo {

  @Override public void check(final ASTNeuron astNeuron) {
    final ASTBody astBodyDecorator = (astNeuron.getBody());
    final Optional<NeuronSymbol> neuronSymbol = (Optional<NeuronSymbol>) astNeuron.getSymbol();
    if (neuronSymbol.isPresent()) {
      astBodyDecorator.getFunctions().forEach(this::checkFunctionName);
    }
    else {
      final String msg = NestmlErrorStrings.getErrorMsgNeuronHasNoSymbol(this,astNeuron.getName());

      Log.error(msg);
    }
  }

  private void checkFunctionName(final ASTFunction astFunction) {

    String funname = astFunction.getName();

    if (astFunction.getEnclosingScope().isPresent()) {
      final Scope scope = astFunction.getEnclosingScope().get();
      final Collection<Symbol> methods = scope.resolveMany(funname, MethodSymbol.KIND);
      if (methods.size() > 1) {
        final String msg = NestmlErrorStrings.getErrorMsgParameterDefinedMultipleTimes(this,funname);

        error(msg, astFunction.get_SourcePositionStart());
      }
    }
    else {
      final String msg = NestmlErrorStrings.getErrorMsgNoScopePresent(this);
      Log.error(msg);
    }

  }

}
