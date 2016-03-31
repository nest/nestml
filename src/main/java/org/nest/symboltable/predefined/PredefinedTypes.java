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

  static  {
    registerSITypes();
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
    return implicitTypes.get("ms");
  }

  public static TypeSymbol getIntegerType() {
    return implicitTypes.get("integer");
  }

  public static TypeSymbol getBufferType() {
    return implicitTypes.get("Buffer");
  }

  private static void registerSITypes() {
    registerType("mV", TypeSymbol.Type.UNIT);
    registerType("pA", TypeSymbol.Type.UNIT);
    registerType("mA", TypeSymbol.Type.UNIT);
    registerType("pF", TypeSymbol.Type.UNIT);
    registerType("pF", TypeSymbol.Type.UNIT);
    registerType("ms", TypeSymbol.Type.UNIT);
    registerType("mm", TypeSymbol.Type.UNIT);
    registerType("nS", TypeSymbol.Type.UNIT);
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

    final MethodSymbol getSumMethod = new MethodSymbol("getSum");
    getSumMethod.addParameterType(getTypeIfExists("ms").get()); // TODO smell
    getSumMethod.setReturnType(getRealType());

    getSumMethod.setDeclaringType(bufferType);
    bufferType.addBuiltInMethod(getSumMethod);
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

  public static Optional<TypeSymbol> getTypeIfExists(final String typeName) {
    if (implicitTypes.containsKey(typeName)) {
      return Optional.of(implicitTypes.get(typeName));
    }
    else {
      return Optional.empty();
    }

  }


}
