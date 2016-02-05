/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;
import de.monticore.symboltable.SymbolKind;
import org.nest.spl._ast.ASTExpr;

import java.util.Objects;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static java.util.Optional.empty;
import static org.nest.utils.NESTMLSymbols.isSetterPresent;

/**
 * Represents variables defined in e.g. variable blocks, functions, etc..
 *
 * @author plotnikov
 */
public class VariableSymbol extends CommonSymbol {
  public static final VariableSymbolKind KIND = new VariableSymbolKind();

  private Optional<ASTExpr> declaringExpression = Optional.empty();

  public enum BlockType {STATE, PARAMETER, INTERNAL, LOCAL, INPUT_BUFFER_CURRENT, INPUT_BUFFER_SPIKE}

  private TypeSymbol type;

  private NeuronSymbol declaringType;

  private boolean isAlias;

  private boolean isLoggable;

  private BlockType blockType;

  private Optional<String> arraySizeParameter = empty();

  public boolean isLoggable() {
    return isLoggable;
  }

  public void setLoggable(boolean loggable) {
    isLoggable = loggable;
  }

  public void setDeclaringExpression(ASTExpr declaringExpression) {
    Objects.requireNonNull(declaringExpression);

    this.declaringExpression = Optional.of(declaringExpression);
  }

  public Optional<ASTExpr> getDeclaringExpression() {
    return declaringExpression;
  }

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

  public boolean isInState() {
    return blockType == BlockType.STATE;
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

  public boolean hasSetter() {
    checkState(getAstNode().isPresent(), "Symbol table must set the AST node.");
    checkArgument(getAstNode().get().getEnclosingScope().isPresent(), "Run symboltable creator.");
    return isSetterPresent(getName(), getType().getName(), getAstNode().get().getEnclosingScope().get());

  }

  public static class VariableSymbolKind implements SymbolKind {

    protected VariableSymbolKind() {
    }

  }
}
