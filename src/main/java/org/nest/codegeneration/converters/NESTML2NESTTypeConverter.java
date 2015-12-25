
package org.nest.codegeneration.converters;

import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * Converts NESTML types to the
 *
 * @author plotnikov
 */
public class NESTML2NESTTypeConverter {
  final PredefinedTypesFactory typesFactory;

  public NESTML2NESTTypeConverter(PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
  }

  public String convert(final TypeSymbol nestmlType) {
    return doConvert(nestmlType);
  }

  public String doConvert(final TypeSymbol nestmlType) {
    if (typesFactory.getStringType().equals(nestmlType)) {
      return "std::string";
    }

    if (typesFactory.getVoidType().equals(nestmlType)) {
      return "void";
    }

    if (typesFactory.getBufferType().equals(nestmlType)) {
      return "nest::RingBuffer";
    }

    if (typesFactory.getBooleanType().equals(nestmlType)) {
      return "bool";
    }

    if (nestmlType.getType() == TypeSymbol.Type.UNIT) {
      return "nest::double_t";
    }

    if (typesFactory.getRealType().equals(nestmlType)) {
      return "nest::double_t";
    }

    if (typesFactory.getIntegerType().equals(nestmlType)) {
      return "int";
    }

    if (nestmlType.getName().contains("Time")) {
      return "nest::Time";
    }
    final String name = nestmlType.getName();

    return name.replaceAll("\\.", "::");
  }
}
