package org.nest.units._visitor;

import com.google.common.base.Preconditions;
import com.sun.org.apache.xpath.internal.operations.Number;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTNESTMLNumericLiteral;
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

  UnitTranslator translator = new UnitTranslator();


  public boolean isSIUnit(String unit){
    if(SIData.getCorrectSIUnits().contains(unit)) {
      return true;
    }
    if(unit.regionMatches(false,0,"e",0,1)){
      try{
        Integer exponent = Integer.parseInt(unit.substring(1));
        return true;
      }catch(NumberFormatException e){
        Preconditions.checkState(false,
            "The unit " + unit + " is not an SI unit.");
      }
    }
    try{
      UnitRepresentation unitRepresentation = new UnitRepresentation(unit);
      return true;
    }catch(Exception e){}
    return false;
  }

/*Verify that the given Unit is valid. Use TranslationVisitor to generate serialization of Unit.
 Overwrite the nodes' "unit" field with the serialization.*/
  public void visit(ASTUnitType node){
      if(node.getUnit().isPresent()){
        String unit = node.getUnit().get();
          Preconditions.checkState(isSIUnit(unit),
              "The unit " + unit + " is not an SI unit.");
      }
    node.setUnit(translator.calculateUnitType(node));
  }
}
