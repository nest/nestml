
package org.nest.codegeneration.converters;

import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

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

    if (nestmlType.getType() == TypeSymbol.Type.UNIT) {
      return "nest::double_t";
    }

    if (PredefinedTypes.getRealType().equals(nestmlType)) {
      return "nest::double_t";
    }

    if (PredefinedTypes.getIntegerType().equals(nestmlType)) {
      return "long";
    }

    if (nestmlType.getName().contains("Time")) {
      return "nest::Time";
    }
    final String name = nestmlType.getName();

    return name.replaceAll("\\.", "::");
  }
}
