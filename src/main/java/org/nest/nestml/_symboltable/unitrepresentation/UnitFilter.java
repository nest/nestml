package org.nest.nestml._symboltable.unitrepresentation;

import java.util.ArrayList;
import java.util.List;

/**
 * Filters units for purposes of the unit system.
 * Set target units via addTarget
 * @author ptraeder
 */
public class UnitFilter {

  private List<UnitRepresentation> targetUnits = new ArrayList<>();

  /**
   *
   * @return the difference of the supplied units magnitude to that of a registered target
   * with matching base. If none exists, return 0
   */
  public int getDifferenceToRegisteredTarget(UnitRepresentation toConvert){
    //find base if exists
    for(UnitRepresentation target: targetUnits){
      if(target.getBase().equals(toConvert.getBase())){
        return toConvert.getMagnitude() - target.getMagnitude();
      }
    }
    return 0;
  }

  /**
   * Adds a new Unit to the list of targets
   * @param newTarget
   * @return true iff there is not a target with the same base already registered
   */
  protected boolean addTarget(UnitRepresentation newTarget) {
    //check that there is not another unit with the same base already in the targets
    for(UnitRepresentation target : targetUnits){
      if(target.getBase().equals(newTarget.getBase())){
        return false;
      }
    }
    targetUnits.add(newTarget);
    return true;
  }
}
