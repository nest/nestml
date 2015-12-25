/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonScopeSpanningSymbol;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents functions, e.g. dynamics, getter/setter, and predefined functions like pow.
 *
 * @author plotnikov
 */
public class MethodSymbol extends CommonScopeSpanningSymbol {

  public final static MethodSymbolKind KIND = new MethodSymbolKind();

  protected TypeSymbol returnType;

  protected NeuronSymbol declaringNeuron;

  protected TypeSymbol declaringType;

  protected List<TypeSymbol> parameters = new ArrayList<TypeSymbol>();

  protected boolean isDynamics = false;

  protected boolean isTimeStep = false;

  protected boolean isMinDelay = false;

  public MethodSymbol(String name) {
    super(name, KIND);
  }

  @Override
  public String toString() {
    return "MethodSymbol(" + getName() + ", #Parameters = " + getParameterTypes().size() + ")";
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

  public boolean isTimeStep() {
    return isTimeStep;
  }

  public void setTimeStep(boolean isTimeStep) {
    this.isTimeStep = isTimeStep;
  }

  public boolean isMinDelay() {
    return isMinDelay;
  }

  public void setMinDelay(boolean isMinDelay) {
    this.isMinDelay = isMinDelay;
  }
}
