/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.ast.ASTNode;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTNeuron;

import java.util.List;
import java.util.Optional;

/**
 * Computes the type of the output for neurons and neuron components.
 *
 * @author plotnikov
 * @since 0.0.1
 */
public class NESTMLInputs {
  public static boolean isSpikeInput(final ASTNode node) {
    final ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(getBodyNode(node));
    final List<ASTInputLine> neuronInputLines = bodyDecorator.getInputLines();
    Optional<ASTInputLine> inputSpikeCandidate = neuronInputLines
        .stream()
        .filter(ASTInputLine::isSpike)
        .findFirst();
    return inputSpikeCandidate.isPresent();
  }

  public static boolean isCurrentInput(final ASTNode node) {
    final ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(getBodyNode(node));
    final List<ASTInputLine> neuronInputLines = bodyDecorator.getInputLines();
    Optional<ASTInputLine> inputSpikeCandidate = neuronInputLines
        .stream()
        .filter(ASTInputLine::isCurrent)
        .findFirst();
    return inputSpikeCandidate.isPresent();
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
