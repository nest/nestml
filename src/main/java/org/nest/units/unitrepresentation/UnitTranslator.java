/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;

import org.nest.units._ast.ASTUnitType;

import java.util.Optional;

/**
 * This visitor translates unit definitions into their internal representation
 * @author ptraeder
 */
public class UnitTranslator {

  public Optional<String> calculateUnitType(final ASTUnitType node){
    final Optional<UnitRepresentation> result = getRecursive(node);
    if (result.isPresent()) {

      return Optional.of(result.get().serialize());
    }
    else {
      return Optional.empty();
    }

  }

  private Optional<UnitRepresentation> getRecursive(final ASTUnitType node){
    if(node.isPow()) {
      final Optional<UnitRepresentation> result = getRecursive(node.getBase().get());
      if (result.isPresent()) {
        return Optional.of(result.get().pow(node.getExponent().get().getValue()));
      }
      else {
        return Optional.empty();
      }

    }
    if(node.isDivOp()) {
      final Optional<UnitRepresentation> left = getRecursive(node.getLeft().get());
      final Optional<UnitRepresentation> right = getRecursive(node.getRight().get());
      if (left.isPresent() && right.isPresent()) {
        return Optional.of(left.get().divideBy(right.get()));
      }
      else {
        return Optional.empty();
      }

    }
    if(node.isTimesOp()) {
      final Optional<UnitRepresentation> left = getRecursive(node.getLeft().get());
      final Optional<UnitRepresentation> right = getRecursive(node.getRight().get());
      if (left.isPresent() && right.isPresent()) {
        return Optional.of(left.get().multiplyBy(right.get()));
      }
      else {
        return Optional.empty();
      }

    }
    if(node.leftParenthesesIsPresent()) {
      return getRecursive(node.getUnitType().get());
    }
    if (node.getUnit().isPresent()) {
      String unit = node.getUnit().get();
      return UnitRepresentation.lookupName(unit);
    }

    throw new UnsupportedOperationException("This situation is impossible through the grammar construction.");
  }

}
