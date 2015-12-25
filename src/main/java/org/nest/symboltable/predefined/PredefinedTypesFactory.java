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
 * Creates implicit types like boolean and nestml specific types like Logger
 *
 * @author plotnikov
 */
public class PredefinedTypesFactory {

  private final static Map<String, TypeSymbol> implicitTypes = Maps.newHashMap();

  public PredefinedTypesFactory() {
    registerType("mV", TypeSymbol.Type.UNIT);
    registerType("pA", TypeSymbol.Type.UNIT);
    registerType("pF", TypeSymbol.Type.UNIT);
    registerType("pF", TypeSymbol.Type.UNIT);
    registerType("ms", TypeSymbol.Type.UNIT);
    registerType("mm", TypeSymbol.Type.UNIT);

    registerType("real", TypeSymbol.Type.PRIMITIVE);
    registerType("integer", TypeSymbol.Type.PRIMITIVE);
    registerType("boolean", TypeSymbol.Type.PRIMITIVE);
    registerType("string", TypeSymbol.Type.PRIMITIVE);
    registerType("void", TypeSymbol.Type.PRIMITIVE);

    registerBufferType();
  }

  private void registerBufferType() {
    final TypeSymbol bufferType
        = new TypeSymbol("Buffer", TypeSymbol.Type.PRIMITIVE);
    implicitTypes.put("Buffer", bufferType);

    final MethodSymbol getSumMethod = new MethodSymbol("getSum");
    getSumMethod.addParameterType(getPredefinedTypeIfExists("ms").get()); // TODO smell
    getSumMethod.setReturnType(getRealType());

    getSumMethod.setDeclaringType(bufferType);
    bufferType.addBuiltInMethod(getSumMethod);
  }

  public TypeSymbol getBooleanType() {
    return implicitTypes.get("boolean");
  }

  // predefined types
  public TypeSymbol getVoidType() {
    return implicitTypes.get("void");
  }

  public TypeSymbol getStringType() {
    return implicitTypes.get("string");
  }

  public TypeSymbol getRealType() {
    return implicitTypes.get("real");
  }

  public TypeSymbol getIntegerType() {
    return implicitTypes.get("integer");
  }

  public TypeSymbol getBufferType() {
    return implicitTypes.get("Buffer");
  }


  private TypeSymbol registerType(String modelName, TypeSymbol.Type type) {
    TypeSymbol typeSymbol = new TypeSymbol(modelName, type);
    typeSymbol.setPackageName("");
    implicitTypes.put(modelName, typeSymbol);
    return typeSymbol;
  }

  public Collection<TypeSymbol> getTypes() {
    return ImmutableList.copyOf(implicitTypes.values());
  }

  public TypeSymbol getType(final String typeName) {
    Optional<TypeSymbol> predefinedType = getPredefinedTypeIfExists(typeName);
    if (predefinedType.isPresent()) {
      return predefinedType.get();
    }
    else {
      throw new RuntimeException("Cannot resolve the predefined type: " + typeName);
    }
  }

  public Optional<TypeSymbol> getPredefinedTypeIfExists(final String typeName) {

    if (implicitTypes.containsKey(typeName)) {
      return Optional.of(implicitTypes.get(typeName));
    }
    else {
      return Optional.empty();
    }

  }

}
