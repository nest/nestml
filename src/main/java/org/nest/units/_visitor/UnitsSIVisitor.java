package org.nest.units._visitor;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.google.common.base.Preconditions;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.units._ast.ASTDatatype;
import org.nest.units._ast.ASTUnitType;
import org.nest.units.unitrepresentation.SIData;

/**
 * Type checking visitor for the UNITS grammar.
 * Verifies that all units used are comprised of SI units.
 * @author ptraeder
 */
public class UnitsSIVisitor implements NESTMLVisitor {

  UnitsTranslationVisitor translator = new UnitsTranslationVisitor();


  public boolean isSIUnit(String unit){
    if(SIData.getCorrectSIUnits().contains(unit)) {
      return true;
    }
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
    translator.handle(node);
    node.setUnit(translator.getResult());
  }

  public void visit(ASTExpr expr){

  }
}
