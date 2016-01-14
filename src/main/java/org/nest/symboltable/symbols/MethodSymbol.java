/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonScopeSpanningSymbol;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Represents functions, e.g. dynamics, getter/setter, and predefined functions like pow.
 *
 * @author plotnikov
 */
public class MethodSymbol extends CommonScopeSpanningSymbol {

  public final static MethodSymbolKind KIND = new MethodSymbolKind();

  private TypeSymbol returnType;
  private NeuronSymbol declaringNeuron;
  private TypeSymbol declaringType;

  private List<TypeSymbol> parameters = new ArrayList<>();
  private boolean isDynamics = false;

  public MethodSymbol(final String name) {
    super(name, KIND);
  }

  @Override
  public String toString() {
    return "MethodSymbol[" + getName() + ", Parameters = " +
        getParameterTypes().stream()
            .map(Object::toString)
            .collect(Collectors.joining(",")) + "]";
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
}
