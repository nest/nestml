/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Maps;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.SIData;
import org.nest.units.unitrepresentation.UnitRepresentation;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;

/**
 * Creates implicit types like boolean and nestml specific
 *
 * @author plotnikov
 */
public class PredefinedTypes {

  private final static Map<String, TypeSymbol> implicitTypes = Maps.newHashMap();

  static {
    registerPrimitiveTypes();
    registerBufferType();
  }

  /**
   * Prevent creation of local copies. Use static getters instead.
   */
  private PredefinedTypes() {

  }

  public static TypeSymbol getBooleanType() {
    return implicitTypes.get("boolean");
  }

  // predefined types
  public static TypeSymbol getVoidType() {
    return implicitTypes.get("void");
  }

  public static TypeSymbol getStringType() {
    return implicitTypes.get("string");
  }

  public static TypeSymbol getRealType() {
    return implicitTypes.get("real");
  }

  public static TypeSymbol getMS() {
    return getTypeIfExists("ms").get();
  }

  public static TypeSymbol getIntegerType() {
    return implicitTypes.get("integer");
  }

  public static TypeSymbol getBufferType() {
    return implicitTypes.get("Buffer");
  }

  public static TypeSymbol getUnitType() {
    return implicitTypes.get("unit");
  }

  private static void registerPrimitiveTypes() {
    registerType("real", TypeSymbol.Type.PRIMITIVE);
    registerType("integer", TypeSymbol.Type.PRIMITIVE);
    registerType("boolean", TypeSymbol.Type.PRIMITIVE);
    registerType("string", TypeSymbol.Type.PRIMITIVE);
    registerType("void", TypeSymbol.Type.PRIMITIVE);
  }

  private static TypeSymbol registerType(String modelName, TypeSymbol.Type type) {
    TypeSymbol typeSymbol = new TypeSymbol(modelName, type);
    typeSymbol.setPackageName("");
    implicitTypes.put(modelName, typeSymbol);
    return typeSymbol;
  }

  private static void registerBufferType() {
    final TypeSymbol bufferType = new TypeSymbol("Buffer", TypeSymbol.Type.BUFFER);
    implicitTypes.put("Buffer", bufferType);

    final MethodSymbol get_sumMethod = new MethodSymbol("get_sum");
    get_sumMethod.addParameterType(getTypeIfExists("ms").get()); // TODO smell
    get_sumMethod.setReturnType(getRealType());

    get_sumMethod.setDeclaringType(bufferType);
    bufferType.addBuiltInMethod(get_sumMethod);
  }

  public static Collection<TypeSymbol> getTypes() {
    return ImmutableList.copyOf(implicitTypes.values());
  }

  public static TypeSymbol getType(final String typeName) {
    Optional<TypeSymbol> predefinedType = getTypeIfExists(typeName);

    if (predefinedType.isPresent()) {
      return predefinedType.get();

    }
    else {
      throw new RuntimeException("Cannot resolve the predefined type: " + typeName);
    }

  }

  /*Return a TypeSymbol for
        -registered types
        -Correct SI Units in name ("ms")
        -Correct Serializations of a UnitRepresentation

        In Case of UNITS always return a TS with serialization as name*/
  public static Optional<TypeSymbol> getTypeIfExists(final String typeName) {
    if (implicitTypes.containsKey(typeName)) {
      return Optional.of(implicitTypes.get(typeName));
    }
    else if (SIData.getCorrectSIUnits().contains(typeName)) {
      Optional<UnitRepresentation> unitRepresentation = UnitRepresentation.lookupName(typeName);
      if (unitRepresentation.isPresent()) {
        registerType(unitRepresentation.get().serialize(), TypeSymbol.Type.UNIT);
        return Optional.of(implicitTypes.get(unitRepresentation.get().serialize()));
      }
      return Optional.empty();
    }
    else {
      try {
        UnitRepresentation unitRepresentation = new UnitRepresentation(typeName);
        registerType(unitRepresentation.serialize(), TypeSymbol.Type.UNIT);
      }
      catch (IllegalStateException e){
        return Optional.empty();
      }
      return Optional.of(implicitTypes.get(typeName));
    }

  }


}
