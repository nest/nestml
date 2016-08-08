package org.nest.units._visitor;

import com.google.common.base.Preconditions;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.units._ast.ASTUnitType;
import org.nest.units.unitrepresentation.SIData;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.units.unitrepresentation.UnitTranslator;

/**
 * Type checking visitor for the UNITS grammar.
 * Verifies that all units used are comprised of SI units.
 * @author ptraeder
 */
public class UnitsSIVisitor implements NESTMLVisitor {

  private UnitTranslator translator = new UnitTranslator();


  private boolean isSIUnit(String unit){
    if(SIData.getCorrectSIUnits().contains(unit)) {
      return true;
    }
    if(unit.regionMatches(false,0,"e",0,1)){
      try{
        Integer.parseInt(unit.substring(1)); // throws exception in case of missformated number
        return true;
      }catch(NumberFormatException e){
        Preconditions.checkState(false,
            "The unit " + unit + " is not an SI unit.");
      }
    }
    try{
      new UnitRepresentation(unit); // throws an exception
      return true;
    }
    catch(Exception e){
      return false;
    }
  }

  /**
   * Verify that the given Unit is valid. Use TranslationVisitor to generate serialization of Unit.
   * Overwrite the nodes' "unit" field with the serialization.
   */
  public void visit(ASTUnitType node){
      if(node.getUnit().isPresent()){
        String unit = node.getUnit().get();
          Preconditions.checkState(isSIUnit(unit),
              "The unit " + unit + " is not an SI unit.");
      }
    node.setUnit(translator.calculateUnitType(node));
  }
}
