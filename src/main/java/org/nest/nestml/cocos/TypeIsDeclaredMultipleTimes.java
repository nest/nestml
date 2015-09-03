/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.monticore.ast.ASTCNode;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.resolving.ResolvedSeveralEntriesException;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Neuron or component is defined several times.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class TypeIsDeclaredMultipleTimes implements NESTMLASTComponentCoCo, NESTMLASTNeuronCoCo {

  public static final String ERROR_CODE = "NESTML_TYPES_DECLARED_MULTIPLE_TIMES";

  public void check(final ASTNeuron neuron) {
      check(neuron.getName(), neuron);
  }

  public void check(final ASTComponent comp) {
    if (comp != null && comp.getName() != null) {
      check(comp.getName(), comp);
    }

  }

  private void check(String name, ASTCNode node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please run symbol table creator");
    try {

      // TODO refactor, document
      node.getEnclosingScope().get().resolve(name, NESTMLNeuronSymbol.KIND);
    }
    catch (ResolvedSeveralEntriesException e) {
      final String msg = "The type '" + name + "' is defined multiple times.";
     error(ERROR_CODE + ":" +  msg, node.get_SourcePositionEnd());
    }

  }

}

