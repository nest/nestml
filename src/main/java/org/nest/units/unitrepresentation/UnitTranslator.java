/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;
import java.util.Optional;

import com.google.common.base.Preconditions;
import org.nest.units._ast.ASTUnitType;

/**
 * @author ptraeder
 * This visitor translates unit definitions into their internal representation
 */
public class UnitTranslator {

  public String calculateUnitType(ASTUnitType node){
    return getRecursive(node).serialize();
  }


  private UnitRepresentation getRecursive(ASTUnitType node){
    if(node.isPow())
      return getRecursive(node.getBase().get()).pow(node.getExponent().get().getValue());
    if(node.isDivOp())
      return getRecursive(node.getLeft().get()).divideBy(getRecursive(node.getRight().get()));
    if(node.isTimesOp())
      return getRecursive(node.getLeft().get()).multiplyBy(getRecursive(node.getRight().get()));
    if(node.leftParenthesesIsPresent())
      return getRecursive(node.getUnitType().get());

    String unit = node.getUnit().get();
    Optional<UnitRepresentation> thisUnit = UnitRepresentation.lookupName(unit);
    Preconditions.checkState(thisUnit.isPresent());
    return thisUnit.get();
  }
}
