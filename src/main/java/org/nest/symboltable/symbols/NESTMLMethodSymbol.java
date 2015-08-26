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
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLMethodSymbol extends CommonScopeSpanningSymbol {

  public final static NESTMLMethodSymbolKind KIND = new NESTMLMethodSymbolKind();

  protected NESTMLTypeSymbol returnType;

  protected NESTMLNeuronSymbol declaringNeuron;

  protected NESTMLTypeSymbol declaringType;

  protected List<NESTMLTypeSymbol> parameters = new ArrayList<NESTMLTypeSymbol>();

  protected boolean isDynamics = false;

  protected boolean isTimeStep = false;

  protected boolean isMinDelay = false;

  public NESTMLMethodSymbol(String name) {
    super(name, KIND);
  }

  @Override
  public String toString() {
    return "NESTMLMethodSymbol(" + getName() + ", #Parameters = " + getParameterTypes().size() + ")";
  }

  public NESTMLTypeSymbol getReturnType() {
    return returnType;
  }

  public void setReturnType(NESTMLTypeSymbol returnType) {
    this.returnType = returnType;
  }

  public NESTMLNeuronSymbol getDeclaringNeuron() {
    return declaringNeuron;
  }

  public void setDeclaringType(NESTMLNeuronSymbol declaringType) {
    this.declaringNeuron = declaringType;
  }

  public NESTMLTypeSymbol getDeclaringType() {
    return declaringType;
  }

  public void setDeclaringType(NESTMLTypeSymbol declaringType) {
    this.declaringType = declaringType;
  }

  public List<NESTMLTypeSymbol> getParameterTypes() {
    return parameters;
  }

  public void addParameterType(NESTMLTypeSymbol parameter) {
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
