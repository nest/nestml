/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonScopeSpanningSymbol;
import de.monticore.symboltable.SymbolKind;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Represents functions, e.g. dynamics, getter/setter, and predefined functions like pow.
 *
 * @author plotnikov
 */
public class MethodSymbol extends CommonScopeSpanningSymbol {
  public final static MethodSymbolKind KIND = new MethodSymbolKind();

  private TypeSymbol returnType;
  private TypeSymbol declaringType;
  private NeuronSymbol declaringNeuron;
  private List<TypeSymbol> parameters = new ArrayList<>();
  private boolean isDynamics = false;
  private Optional<String> unitDescriptor;

  public MethodSymbol(final String name) {
    super(name, KIND);
  }

  public MethodSymbol(final MethodSymbol other) {
    this(other.getName());
    this.returnType = other.returnType;
    this.declaringType = other.declaringType;
    this.declaringNeuron = other.declaringNeuron;
    this.isDynamics = other.isDynamics;
    parameters.addAll(other.getParameterTypes());
  }

  @Override
  public String toString() {
    return "MethodSymbol[" + getName() + ", Parameters = " +
        getParameterTypes().stream()
            .map(Object::toString)
            .collect(Collectors.joining(",")) + "]";
  }

  public Optional<String> getUnitDescriptor() {
    return unitDescriptor;
  }

  public void setUnitDescriptor(String unitDescriptor) {
    this.unitDescriptor = Optional.of(unitDescriptor);
  }

  public TypeSymbol getReturnType() {
    return returnType;
  }

  public void setReturnType(TypeSymbol returnType) {
    this.returnType = returnType;
  }

  public NeuronSymbol getDeclaringNeuron() {
    return declaringNeuron;
  }

  public void setDeclaringType(NeuronSymbol declaringType) {
    this.declaringNeuron = declaringType;
  }

  public TypeSymbol getDeclaringType() {
    return declaringType;
  }

  public void setDeclaringType(TypeSymbol declaringType) {
    this.declaringType = declaringType;
  }

  public List<TypeSymbol> getParameterTypes() {
    return parameters;
  }

  public void addParameterType(TypeSymbol parameter) {
    this.parameters.add(parameter);
  }

  public boolean isDynamics() {
    return isDynamics;
  }

  public void setDynamics(boolean isDynamics) {
    this.isDynamics = isDynamics;
  }

  @Override
  public boolean equals(Object obj)
  {
    if (obj == null) {
      return false;
    }
    if (getClass() != obj.getClass()) {
      return false;
    }
    final MethodSymbol other = (MethodSymbol) obj;

    return   com.google.common.base.Objects.equal(this.returnType, other.returnType)
        && com.google.common.base.Objects.equal(this.getName(), other.getName())
        && com.google.common.base.Objects.equal(this.declaringType, other.declaringType)
        && com.google.common.base.Objects.equal(this.declaringNeuron, other.declaringNeuron)
        && isDynamics == other.isDynamics;

  }

  @Override
  public int hashCode()
  {
    return com.google.common.base.Objects.hashCode(
        this.getName(), this.returnType, declaringType, declaringNeuron, isDynamics, this.parameters);
  }

  private static class MethodSymbolKind implements SymbolKind {
    MethodSymbolKind() {
    }
  }

}
