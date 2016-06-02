package org.nest.units.prettyprinter;

import org.nest.units._ast.ASTUnitType;
import org.nest.units._visitor.UnitsVisitor;
import org.nest.utils.PrettyPrinterBase;

/**
 * @author ptraeder
 */
public class UnitsPrettyPrinter extends PrettyPrinterBase implements UnitsVisitor {


  public void visit(ASTUnitType node){
    if(node.isDivOp()){
      String numerator = node.getLeft().get().getUnit().get();
      String denominator = node.getRight().get().getUnit().get();
      print(numerator+"/"+denominator);
    }
  }
}
