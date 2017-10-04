/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTInputLine;

import java.util.List;
import java.util.Optional;

/**
 * Computes the type of the output for neurons and neuron components.
 *
 * @author plotnikov
 */
public class ASTInputs {

  public static boolean isSpikeInput(final ASTNeuron node) {
    final List<ASTInputLine> neuronInputLines = node.getInputLines();
    Optional<ASTInputLine> inputSpikeCandidate = neuronInputLines
        .stream()
        .filter(ASTInputLine::isSpike)
        .findFirst();
    return inputSpikeCandidate.isPresent();
  }

  public static boolean isCurrentInput(final ASTNeuron node) {
    final List<ASTInputLine> neuronInputLines = node.getInputLines();
    Optional<ASTInputLine> inputSpikeCandidate = neuronInputLines
        .stream()
        .filter(ASTInputLine::isCurrent)
        .findFirst();
    return inputSpikeCandidate.isPresent();
  }


}
