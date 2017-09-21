/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.ast.ASTNode;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTNeuron;

import java.util.List;
import java.util.Optional;

/**
 * Computes the type of the output for neurons and neuron components.
 *
 * @author plotnikov
 */
public class ASTInputs {
  public static boolean isSpikeInput(final ASTNode node) {
    final ASTBody bodyDecorator = (getBodyNode(node));
    final List<ASTInputLine> neuronInputLines = bodyDecorator.getInputLines();
    Optional<ASTInputLine> inputSpikeCandidate = neuronInputLines
        .stream()
        .filter(ASTInputLine::spikeIsPresent)
        .findFirst();
    return inputSpikeCandidate.isPresent();
  }

  public static boolean isCurrentInput(final ASTNode node) {
    final ASTBody bodyDecorator = (getBodyNode(node));
    final List<ASTInputLine> neuronInputLines = bodyDecorator.getInputLines();
    Optional<ASTInputLine> inputSpikeCandidate = neuronInputLines
        .stream()
        .filter(ASTInputLine::currentIsPresent)
        .findFirst();
    return inputSpikeCandidate.isPresent();
  }

  private static ASTBody getBodyNode(ASTNode node) {
    ASTBody bodyElement;// TODO probably introduce a grammar rule for this
    if (node instanceof ASTNeuron) {
      bodyElement = ((ASTNeuron) node).getBody();
    }
    else {
      throw new RuntimeException("Unexpected instance of the neuron element");
    }
    return bodyElement;
  }

}
