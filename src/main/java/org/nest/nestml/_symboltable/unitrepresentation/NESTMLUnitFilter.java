package org.nest.nestml._symboltable.unitrepresentation;

/**
 * @author ptraeder
 */
public class NESTMLUnitFilter extends UnitFilter {
  NESTMLUnitFilter(){
    addTarget(UnitRepresentation.lookupName("ms").get());
    addTarget(UnitRepresentation.lookupName("pF").get());
    addTarget(UnitRepresentation.lookupName("mV").get());
    addTarget(UnitRepresentation.lookupName("pA").get());
    addTarget(UnitRepresentation.lookupName("nS").get());
    addTarget(UnitRepresentation.lookupName("GOhm").get());
  }
}
