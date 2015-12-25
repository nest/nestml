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
 * Represents variables defined in e.g. variable blocks, functions, etc..
 *
 * @author plotnikov
 */
public class VariableSymbol extends CommonSymbol {

  public enum BlockType {STATE, PARAMETER, INTERNAL, LOCAL, INPUT_BUFFER_CURRENT, INPUT_BUFFER_SPIKE}

  public static final VariableSymbolKind KIND = new VariableSymbolKind();

  private TypeSymbol type;

  private NeuronSymbol declaringType;

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

  public VariableSymbol(String name) {
    super(name, KIND);
    setBlockType(BlockType.LOCAL);
  }

  @Override
  public String toString() {
    return "VariableSymbol(" + getName() + ", " + getType() + ", "
        + getBlockType() + "," + arraySizeParameter + ")";
  }

  public TypeSymbol getType() {
    return type;
  }

  public void setType(TypeSymbol type) {
    this.type = type;
  }

  public void setDeclaringType(NeuronSymbol declaringType) {
    this.declaringType = declaringType;
  }

  public NeuronSymbol getDeclaringType() {
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
