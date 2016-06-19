package org.nest.units._visitor;
import java.util.Optional;
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

  private int getMagnitude(String pre){
    return SIData.getPrefixMagnitudes().get(pre);
  }

  private Optional<UnitRepresentation> getUnitRepresentation(String unit){
    for (String pre: SIData.getSIPrefixes()){
      if(pre.regionMatches(false,0,unit,0,pre.length())){
        //See if remaining unit name matches a valid SI Unit. Since some prefixes are not unique
        String remainder = unit.substring(pre.length());
        if(SIData.getBaseRepresentations().containsKey(remainder)){
          int magnitude = getMagnitude(pre);
          UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(remainder));
          result.addMagnitude(magnitude);
          return Optional.of(result);
        }
      }
    }
    //should never happen
    return Optional.empty();
  }

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
        Optional<UnitRepresentation> thisUnit = getUnitRepresentation(unit);
        if (thisUnit.isPresent()) {
          lastResult = thisUnit.get();
        }
      }
    }
}
