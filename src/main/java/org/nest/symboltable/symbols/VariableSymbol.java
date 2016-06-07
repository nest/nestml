/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.SymbolKind;
import org.nest.commons._ast.ASTExpr;

import java.util.Objects;
import java.util.Optional;

import static com.google.common.base.Preconditions.*;
import static org.nest.utils.NESTMLSymbols.isSetterPresent;

/**
 * Represents variables defined in e.g. variable blocks, functions, etc..
 *
 * @author plotnikov
 */
public class VariableSymbol extends CommonSymbol {


  public static final VariableSymbolKind KIND = new VariableSymbolKind();

  private ASTExpr declaringExpression = null;

  private TypeSymbol type;

  private NeuronSymbol declaringType;

  private boolean isAlias;

  private boolean isLoggable;

  private BlockType blockType;

  private String arraySizeParameter = null;

  public boolean isBuffer() {
    return blockType == BlockType.INPUT_BUFFER_CURRENT || blockType == BlockType.INPUT_BUFFER_SPIKE;
  }

  public boolean isLoggable() {
    // TODO: check whether the logic is correct. At the moment, the vector datatypes are not supported by the code
    // generator.
    return isLoggable && !isVector();
  }

  public void setLoggable(boolean loggable) {
    isLoggable = loggable;
  }

  public void setDeclaringExpression(final ASTExpr declaringExpression) {
    Objects.requireNonNull(declaringExpression);

    this.declaringExpression = declaringExpression;
  }

  public VariableSymbol(String name) {
    super(name, KIND);
    setBlockType(BlockType.LOCAL);
  }

  public Optional<ASTExpr> getDeclaringExpression() {
    return Optional.ofNullable(declaringExpression);
  }

  public Optional<String> getVectorParameter() {
    return Optional.ofNullable(arraySizeParameter);
  }

  public void setVectorParameter(final String arraySizeParameter) {
    checkNotNull(arraySizeParameter);
    this.arraySizeParameter = arraySizeParameter;
  }

  @Override
  public String toString() {
    return "VariableSymbol(" + getName() + ", " + getType() + ", "
        + getBlockType() + "," + "array parameter: " + arraySizeParameter + ")";
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

  public boolean isVector() {
    return getVectorParameter().isPresent();
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

  public String printComment() {
    final StringBuffer output = new StringBuffer();
    if(getAstNode().isPresent()) {
      getAstNode().get().get_PreComments().forEach(comment -> output.append(comment.getText()).append(" "));
      getAstNode().get().get_PostComments().forEach(comment -> output.append(comment.getText()).append(" "));
    }

    return output.toString();
  }

  public static VariableSymbol resolve(final String variableName, final Scope scope) {
    final Optional<VariableSymbol> variableSymbol = scope.resolve(variableName, VariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + variableName);
    return variableSymbol.get();
  }

  public static Optional<VariableSymbol> resolveIfExists(final String variableName, final Scope scope) {
    return scope.resolve(variableName, VariableSymbol.KIND);
  }

  /**
   * Technical class for the symobol table.
   */
  static private class VariableSymbolKind implements SymbolKind {

    VariableSymbolKind() {
    }

  }

  public enum BlockType {
    STATE,
    PARAMETER,
    INTERNAL,
    LOCAL,
    INPUT_BUFFER_CURRENT,
    INPUT_BUFFER_SPIKE,
    OUTPUT
  }

}
