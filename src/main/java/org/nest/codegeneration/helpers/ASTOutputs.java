/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.ast.ASTNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutputBlock;

import java.util.List;

/**
 * Computes the type of the output for neurons and neuron components.
 *
 * @author plotnikov
 */
public class ASTOutputs {
  public static boolean isOutputEventPresent(final ASTNeuron astNeuron) {
    return !astNeuron.getOutputBlocks().isEmpty();
  }

  public static String printOutputEvent(final ASTNeuron astNeuron) {
    final List<ASTOutputBlock> neuronOutputs = astNeuron.getOutputBlocks();
    if (!neuronOutputs.isEmpty()) {
      ASTOutputBlock output = neuronOutputs.get(0);

      if (output.isSpike()) {
        return "nest::SpikeEvent";
      }
      else if (output.isCurrent()) {
        return "nest::CurrentEvent";
      }
      else {
        throw new RuntimeException("Unexpected output type. Must be current or spike.");
      }
    }
    else {
      return "none";
    }
  }

  private static ASTNeuron getBodyNode(ASTNode node) {
    ASTNeuron bodyElement;// TODO probably introduce a grammar rule for this

    if (node instanceof ASTNeuron) {
      bodyElement = ((ASTNeuron) node);
    }
    else {
      throw new RuntimeException("Unexpected instance of the neuron element");
    }
    return bodyElement;
  }
}
