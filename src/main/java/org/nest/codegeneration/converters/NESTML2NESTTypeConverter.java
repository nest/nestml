
package org.nest.codegeneration.converters;

import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.TypeSymbol;

/**
 * Converts NESTML types to the
 *
 * @author plotnikov
 */
public class NESTML2NESTTypeConverter {

  public String convert(final TypeSymbol nestmlType) {
    return doConvert(nestmlType);
  }

  private String doConvert(final TypeSymbol nestmlType) {
    if (PredefinedTypes.getStringType().equals(nestmlType)) {
      return "std::string";
    }

    if (PredefinedTypes.getVoidType().equals(nestmlType)) {
      return "void";
    }

    if (PredefinedTypes.getBufferType().equals(nestmlType)) {
      return "nest::RingBuffer";
    }

    if (PredefinedTypes.getBooleanType().equals(nestmlType)) {
      return "bool";
    }

    if (nestmlType.getType() == TypeSymbol.Type.UNIT || PredefinedTypes.getRealType().equals(nestmlType)) {
      return "double";
    }

    if (PredefinedTypes.getIntegerType().equals(nestmlType)) {
      return "long";
    }

    if (nestmlType.getName().contains("Time")) {
      return "nest::Time";
    }
    final String name = nestmlType.getName();
    PredefinedTypes.getRealType().equals(nestmlType);
    return name.replaceAll("\\.", "::");
  }
}
