/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.ast.ASTNode;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;

import java.util.List;

import static com.google.common.base.Preconditions.checkState;

/**
 * Computes the type of the output for neurons and neuron components.
 *
 * @author plotnikov
 * @since 0.0.1
 */
public class NESTMLOutputs {
  public static boolean isOutputEventPresent(final ASTNode node) {
    final ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(getBodyNode(node));
    return !bodyDecorator.getOutputs().isEmpty();
  }

  public static String printOutputEvent(final ASTNode node) {
    final ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(getBodyNode(node));
    final List<ASTOutput> neuronOutputs = bodyDecorator.getOutputs();
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
