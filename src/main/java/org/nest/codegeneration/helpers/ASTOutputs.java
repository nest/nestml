/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.ast.ASTNode;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;

import java.util.List;

/**
 * Computes the type of the output for neurons and neuron components.
 *
 * @author plotnikov
 */
public class ASTOutputs {
  public static boolean isOutputEventPresent(final ASTBody astBody) {
    return !astBody.getOutputs().isEmpty();
  }

  public static String printOutputEvent(final ASTBody astBody) {
    final List<ASTOutput> neuronOutputs = astBody.getOutputs();
    if (!neuronOutputs.isEmpty()) {
      ASTOutput output = neuronOutputs.get(0);

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

  private static ASTBody getBodyNode(ASTNode node) {
    ASTBody bodyElement;// TODO probably introduce a grammar rule for this
    if  (node instanceof ASTComponent) {
      bodyElement = ((ASTComponent) node).getBody();
    }
    else if (node instanceof ASTNeuron) {
      bodyElement = ((ASTNeuron) node).getBody();
    }
    else {
      throw new RuntimeException("Unexpected instance of the neuron element");
    }
    return bodyElement;
  }
}
