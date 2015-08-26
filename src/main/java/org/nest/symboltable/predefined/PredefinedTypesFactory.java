/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Maps;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;

/**
 * Creates implicit types like boolean and nestml specific types like Logger
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class PredefinedTypesFactory {

  private final static Map<String, NESTMLTypeSymbol> implicitTypes = Maps.newHashMap();

  public PredefinedTypesFactory() {
    registerType("mV", NESTMLTypeSymbol.Type.UNIT);
    registerType("pA", NESTMLTypeSymbol.Type.UNIT);
    registerType("pF", NESTMLTypeSymbol.Type.UNIT);
    registerType("pF", NESTMLTypeSymbol.Type.UNIT);
    registerType("ms", NESTMLTypeSymbol.Type.UNIT);
    registerType("mm", NESTMLTypeSymbol.Type.UNIT);

    registerType("real", NESTMLTypeSymbol.Type.PRIMITIVE);
    registerType("integer", NESTMLTypeSymbol.Type.PRIMITIVE);
    registerType("boolean", NESTMLTypeSymbol.Type.PRIMITIVE);
    registerType("string", NESTMLTypeSymbol.Type.PRIMITIVE);
    registerType("void", NESTMLTypeSymbol.Type.PRIMITIVE);

    registerBufferType();
  }

  private void registerBufferType() {
    final NESTMLTypeSymbol bufferType
        = new NESTMLTypeSymbol("Buffer", NESTMLTypeSymbol.Type.PRIMITIVE);
    implicitTypes.put("Buffer", bufferType);

    final NESTMLMethodSymbol getSumMethod = new NESTMLMethodSymbol("getSum");
    getSumMethod.addParameterType(getPredefinedTypeIfExists("ms").get()); // TODO smell
    getSumMethod.setReturnType(getRealType());

    getSumMethod.setDeclaringType(bufferType);
    bufferType.addBuiltInMethod(getSumMethod);
  }

  public NESTMLTypeSymbol getBooleanType() {
    return implicitTypes.get("boolean");
  }

  // predefined types
  public NESTMLTypeSymbol getVoidType() {
    return implicitTypes.get("void");
  }

  public NESTMLTypeSymbol getStringType() {
    return implicitTypes.get("string");
  }

  public NESTMLTypeSymbol getRealType() {
    return implicitTypes.get("real");
  }

  public NESTMLTypeSymbol getIntegerType() {
    return implicitTypes.get("integer");
  }

  public NESTMLTypeSymbol getBufferType() {
    return implicitTypes.get("Buffer");
  }


  private NESTMLTypeSymbol registerType(String modelName, NESTMLTypeSymbol.Type type) {
    NESTMLTypeSymbol typeSymbol = new NESTMLTypeSymbol(modelName, type);
    typeSymbol.setPackageName("");
    implicitTypes.put(modelName, typeSymbol);
    return typeSymbol;
  }

  public Collection<NESTMLTypeSymbol> getTypes() {
    return ImmutableList.copyOf(implicitTypes.values());
  }

  public NESTMLTypeSymbol getType(final String typeName) {
    Optional<NESTMLTypeSymbol> predefinedType = getPredefinedTypeIfExists(typeName);
    if (predefinedType.isPresent()) {
      return predefinedType.get();
    }
    else {
      throw new RuntimeException("Cannot resolve the predefined type: " + typeName);
    }
  }

  public Optional<NESTMLTypeSymbol> getPredefinedTypeIfExists(final String typeName) {

    if (implicitTypes.containsKey(typeName)) {
      return Optional.of(implicitTypes.get(typeName));
    }
    else {
      return Optional.empty();
    }

  }

}
