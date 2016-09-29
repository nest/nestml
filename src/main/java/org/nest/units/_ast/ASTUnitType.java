package org.nest.units._ast;

/**
 * @author ptraeder
 */
public class ASTUnitType extends ASTUnitTypeTOP{
  private String serializedUnit;

  public ASTUnitType(org.nest.units._ast.ASTUnitType unitType,
      org.nest.units._ast.ASTUnitType base,
      de.monticore.literals.literals._ast.ASTIntLiteral exponent,
      org.nest.units._ast.ASTUnitType left,
      org.nest.units._ast.ASTUnitType right,
      String unit,
      String leftParentheses,
      String rightParentheses,
      boolean divOp,
      boolean timesOp,
      boolean pow ){
    super(unitType,base,exponent,left,right,unit,leftParentheses,rightParentheses,divOp,timesOp,pow);
  }

  public ASTUnitType() {
  }

  public String getSerializedUnit() {
    return serializedUnit;
  }

  public void setSerializedUnit(String serializedUnit) {
    this.serializedUnit = serializedUnit;
  }
}
