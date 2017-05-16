/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.resolving.ResolvedSeveralEntriesException;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.symboltable.symbols.NeuronSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Neuron or component is defined several times.
 *
 * @author ippen, plotnikov
 */
public class TypeIsDeclaredMultipleTimes implements NESTMLASTNeuronCoCo {

  public void check(final ASTNeuron neuron) {
      check(neuron.getName(), neuron);
  }

  private void check(String name, ASTNode node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please run symbol table creator");
    try {

      // TODO refactor, document
      node.getEnclosingScope().get().resolve(name, NeuronSymbol.KIND);
    }
    catch (ResolvedSeveralEntriesException e) {
      final String msg = NestmlErrorStrings.getErrorMsg(this, name);

     error(msg, node.get_SourcePositionEnd());
    }

  }

}

