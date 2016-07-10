package org.nest.units.prettyprinter;

import static com.google.common.base.Preconditions.checkNotNull;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

/**
 * prints the serialized Unit typenames as readable text.
 * @author ptraeder
 */
public class UnitsPrettyPrinter {
  public String print(TypeSymbol type) {
    checkNotNull(type);
    if (type.getType().equals(TypeSymbol.Type.UNIT)) {
      UnitRepresentation unitRepresentation = new UnitRepresentation(type.getName());
      return unitRepresentation.prettyPrint();
    }
    return type.getName(); //primitive and buffer
  }
}

