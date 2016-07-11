package org.nest.units.prettyprinter;

import static com.google.common.base.Preconditions.checkNotNull;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units._ast.ASTDatatype;
import org.nest.units.unitrepresentation.UnitRepresentation;

/**
 * prints the serialized Unit typenames as readable text.
 * @author ptraeder
 */
public class TypesPrettyPrinter {
  public String print(TypeSymbol type) {
    checkNotNull(type);
    if (type.getType().equals(TypeSymbol.Type.UNIT)) {
      UnitRepresentation unitRepresentation = new UnitRepresentation(type.getName());
      return unitRepresentation.prettyPrint();
    }
    return type.getName(); //primitive and buffer
  }
  public String print(ASTDatatype type) {
    checkNotNull(type);
    if (type.getUnitType().isPresent() && type.getUnitType().get().getUnit().isPresent()) {
      UnitRepresentation unitRepresentation = new UnitRepresentation(type.getUnitType().get().getUnit().get());
      return unitRepresentation.prettyPrint();
    }
    String typeName = null;
    if (type.isBoolean()) {
      typeName = "boolean";
    }
    else if (type.isInteger()) {
      typeName = "integer";
    }
    else if (type.isReal()) {
      typeName = "real";
    }
    else if (type.isString()) {
      typeName = "string";
    }
    else if (type.isVoid()) {
      typeName = "void";
    }
    return typeName;
  }
}

