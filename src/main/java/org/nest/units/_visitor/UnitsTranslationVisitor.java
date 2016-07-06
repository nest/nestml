package org.nest.units._visitor;
import java.util.Optional;

import com.google.common.base.Preconditions;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.units._ast.ASTUnitType;
import org.nest.units.unitrepresentation.SIData;
import org.nest.units.unitrepresentation.UnitRepresentation;

/**
 * @author ptraeder
 * This visitor translates unit definitions into their internal representation
 */
public class UnitsTranslationVisitor implements NESTMLVisitor,UnitsVisitor {

  UnitRepresentation left,right,base;
  UnitRepresentation lastResult;

  public String getResult(){
    return lastResult.toString();
  }

  public void handle(org.nest.units._ast.ASTUnitType node) {
    getRealThis().traverse(node);
    getRealThis().visit(node);
    getRealThis().endVisit(node);
  }

  public void traverse(org.nest.units._ast.ASTUnitType node) {
    if (node.getUnitType().isPresent()) {
      node.getUnitType().get().accept(getRealThis());
    }
    if (node.getBase().isPresent()) {
      node.getBase().get().accept(getRealThis());
      base = lastResult;
    }
    if (node.getExponent().isPresent()) {
      node.getExponent().get().accept(getRealThis());
    }
    if (node.getLeft().isPresent()) {
      node.getLeft().get().accept(getRealThis());
      left = lastResult;
    }
    if (node.getRight().isPresent()) {
      node.getRight().get().accept(getRealThis());
      right = lastResult;
    }
  }

  public void visit(ASTUnitType node){
      if (node.isDivOp()) {
        lastResult = left.divideBy(right);
        //variableSymbol.setUnitDescriptor(lastResult.toString());
      }
      else if (node.isPow()) {
        int exponent = node.getExponent().get().getValue();
        lastResult = base.pow(exponent);
      }
      else if (node.isTimesOp()) {
        lastResult = left.multiplyBy(right);
      }
      else {
        String unit = node.getUnit().get();
        Optional<UnitRepresentation> thisUnit = UnitRepresentation.lookupName(unit);
        Preconditions.checkState(thisUnit.isPresent());
        lastResult = thisUnit.get();
      }
    }
}
