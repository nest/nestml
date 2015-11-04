/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;

import java.util.Optional;

import static java.util.Optional.empty;

/**
 * Represents variables in neuron and functions.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLVariableSymbol extends CommonSymbol {

  public enum BlockType {STATE, PARAMETER, INTERNAL, LOCAL, INPUT_BUFFER_CURRENT, INPUT_BUFFER_SPIKE}

  public static final NESTMLVariableSymbolKind KIND = new NESTMLVariableSymbolKind();

  private NESTMLTypeSymbol type;

  private NESTMLNeuronSymbol declaringType;

  private boolean isAlias;

  private boolean isHidden;

  private BlockType blockType;

  private Optional<String> arraySizeParameter = empty();

  public Optional<String> getArraySizeParameter() {
    return arraySizeParameter;
  }

  public void setArraySizeParameter(String arraySizeParameter) {
    this.arraySizeParameter = Optional.of(arraySizeParameter);
  }

  public NESTMLVariableSymbol(String name) {
    super(name, KIND);
    setBlockType(BlockType.LOCAL);
  }

  @Override
  public String toString() {
    return "NESTMLVariableSymbol(" + getName() + ", " + getType() + ", "
        + getBlockType() + "," + arraySizeParameter + ")";
  }

  public NESTMLTypeSymbol getType() {
    return type;
  }

  public void setType(NESTMLTypeSymbol type) {
    this.type = type;
  }

  public void setDeclaringType(NESTMLNeuronSymbol declaringType) {
    this.declaringType = declaringType;
  }

  public NESTMLNeuronSymbol getDeclaringType() {
    return declaringType;
  }


  public boolean isAlias() {
    return isAlias;
  }

  public void setAlias(boolean isAlias) {
    this.isAlias = isAlias;
  }

  public BlockType getBlockType() {
    return blockType;
  }

  public void setBlockType(BlockType blockType) {
    this.blockType = blockType;
  }

  public boolean isHidden() {
    return isHidden;
  }

  public void setHidden(boolean isHidden) {
    this.isHidden = isHidden;
  }

}
