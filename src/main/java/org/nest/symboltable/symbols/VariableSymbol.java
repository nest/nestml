/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.SymbolKind;
import org.nest.codegeneration.helpers.ASTBuffers;
import org.nest.commons._ast.ASTExpr;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.utils.AstUtils;

import java.util.Objects;
import java.util.Optional;

import static com.google.common.base.Preconditions.*;
import static org.nest.utils.AstUtils.getVectorizedVariable;
import static org.nest.symboltable.NESTMLSymbols.isSetterPresent;

/**
 * Represents variables defined in e.g. variable blocks, functions, etc..
 *
 * @author plotnikov
 */
public class VariableSymbol extends CommonSymbol {
  public static final VariableSymbolKind KIND = new VariableSymbolKind();
  private ASTExpr declaringExpression = null;

  private ASTExpr odeDeclaration = null;

  private TypeSymbol type;
  private NeuronSymbol declaringType;
  private boolean isAlias;
  private boolean isLoggable;
  private BlockType blockType;
  private String arraySizeParameter = null;
  private boolean conductanceBased = false;

  public boolean isBuffer() {
    return blockType == BlockType.INPUT_BUFFER_CURRENT || blockType == BlockType.INPUT_BUFFER_SPIKE;
  }

  @SuppressWarnings({"unused"}) // used in templates
  public boolean isLoggable() {
    // TODO: check whether the logic is correct. At the moment, the vector datatypes are not supported by the code
    // generator.
    return isLoggable && !isVector();
  }
  public Optional<ASTExpr> getOdeDeclaration() {
    return Optional.ofNullable(odeDeclaration);
  }

  public void setOdeDeclaration(final ASTExpr odeDeclaration) {
    this.odeDeclaration = odeDeclaration;
  }

  public boolean definedByODE() {
    return odeDeclaration != null;
  }

  public void setRecordable(boolean loggable) {
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

  @Override
  public String toString() {
    return "VariableSymbol(" + getName() + ", " + getType() + ", "
           + getBlockType() + "," + "array parameter: " + arraySizeParameter
           + (getAstNode().isPresent()?getAstNode().get().get_SourcePositionStart():"") + ")";
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

  public boolean isSpikeBuffer() {
    if (getAstNode().isPresent() && getAstNode().get() instanceof ASTInputLine) {
      final ASTInputLine astInputLine = (ASTInputLine) getAstNode().get();
      return astInputLine.isSpike();
    }
    return false;
  }

  public boolean isCurrentBuffer() {
    if (getAstNode().isPresent() && getAstNode().get() instanceof ASTInputLine) {
      final ASTInputLine astInputLine = (ASTInputLine) getAstNode().get();
      return astInputLine.isCurrent();
    }
    return false;
  }

  public boolean isExcitatory() {
    if (getAstNode().isPresent() && getAstNode().get() instanceof ASTInputLine) {
      final ASTInputLine astInputLine = (ASTInputLine) getAstNode().get();
      return ASTBuffers.isExcitatory(astInputLine);
    }
    return false;
  }

  public boolean isInhibitory() {
    if (getAstNode().isPresent() && getAstNode().get() instanceof ASTInputLine) {
      final ASTInputLine astInputLine = (ASTInputLine) getAstNode().get();
      return ASTBuffers.isInhibitory(astInputLine);
    }
    return false;
  }

  public boolean isInhAndExc() {
    if (getAstNode().isPresent() && getAstNode().get() instanceof ASTInputLine) {
      final ASTInputLine astInputLine = (ASTInputLine) getAstNode().get();
      return AstUtils.isInhExc(astInputLine);
    }
    return false;
  }

  public boolean isVector() {
    if (blockType != BlockType.SHAPE) {
      return getVectorParameter().isPresent();
    }
    else {
      // declaring expression exists by construction from symbol table creator
      // there no shape without declaring expression
      return getVectorizedVariable(getDeclaringExpression().get(), getEnclosingScope()).isPresent();
    }

  }

  public Optional<String> getVectorParameter() {
    if (blockType != BlockType.SHAPE) {
      return Optional.ofNullable(arraySizeParameter);
    }
    else {
      final Optional<VariableSymbol> vectorizedVariable = getVectorizedVariable(getDeclaringExpression().get(), getEnclosingScope());
      if (vectorizedVariable.isPresent()) {
        return vectorizedVariable.get().getVectorParameter();
      }
      else {
        return Optional.empty();
      }
    }

  }

  public void setVectorParameter(final String arraySizeParameter) {
    checkNotNull(arraySizeParameter);
    this.arraySizeParameter = arraySizeParameter;
  }

  public boolean isState() {
    return blockType == BlockType.STATE;
  }

  public boolean isInEquation() {
    return blockType == BlockType.EQUATION;
  }

  public boolean isParameters () {
    return blockType == BlockType.PARAMETER;
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

  @SuppressWarnings({"unused"}) // used in templates
  public boolean hasSetter() {
    checkState(getAstNode().isPresent(), "Symbol table must set the AST node.");
    checkArgument(getAstNode().get().getEnclosingScope().isPresent(), "Run symboltable creator.");

    return isSetterPresent(getName(), getType().getName(), getAstNode().get().getEnclosingScope().get());
  }

  @SuppressWarnings({"unused"}) // used in templates
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

  public boolean isConductanceBased() {
    return conductanceBased;
  }

  public void setConductanceBased(boolean conductanceBased) {
    this.conductanceBased = conductanceBased;
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
    EQUATION,
    LOCAL,
    INPUT_BUFFER_CURRENT,
    INPUT_BUFFER_SPIKE,
    OUTPUT,
    SHAPE
  }

}
