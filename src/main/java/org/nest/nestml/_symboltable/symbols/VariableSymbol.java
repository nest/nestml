/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.SymbolKind;
import org.nest.codegeneration.helpers.ASTBuffers;
import org.nest.codegeneration.sympy.OdeTransformer;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.utils.AstUtils;

import java.util.Objects;
import java.util.Optional;

import static com.google.common.base.Preconditions.*;
import static org.nest.nestml._symboltable.NestmlSymbols.isGetterPresent;
import static org.nest.nestml._symboltable.NestmlSymbols.isSetterPresent;
import static org.nest.utils.AstUtils.getVectorizedVariable;

/**
 * Represents variables defined in e.g. variable blocks, functions, etc..
 *
 * @author plotnikov
 */
public class VariableSymbol extends CommonSymbol {
  public static final VariableSymbolKind KIND = new VariableSymbolKind();
  private VariableType variableType;
  private BlockType blockType;

  private ASTExpr declaringExpression = null;
  private ASTExpr odeDeclaration = null;
  private TypeSymbol type;
  private boolean isFunction;
  private boolean isRecordable;
  private String arraySizeParameter = null;
  private boolean conductanceBased = false;

  public VariableSymbol(final String name, final BlockType blockType, final VariableType variableType) {
    super(name, KIND);
    this.blockType = blockType;
    this.variableType = variableType;
  }

  public boolean isBuffer() {
    return blockType == BlockType.INPUT;
  }

  @SuppressWarnings({"unused"}) // used in templates
  public boolean isRecordable() {
    // TODO: check whether the logic is correct. At the moment, the vector datatypes are not supported by the code
    // generator.
    return isRecordable && !isVector();
  }

  @SuppressWarnings({"unused"}) // used in templates
  public Optional<ASTExpr> getOdeDeclaration() {
    return Optional.ofNullable(odeDeclaration);
  }

  public void setOdeDeclaration(final ASTExpr odeDeclaration) {
    this.odeDeclaration = odeDeclaration;
  }

  public void setRecordable(boolean loggable) {
    isRecordable = loggable;
  }

  public void setDeclaringExpression(final ASTExpr declaringExpression) {
    Objects.requireNonNull(declaringExpression);

    this.declaringExpression = declaringExpression;
  }

  @SuppressWarnings({"unused"}) // used in templates. must be public.
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
    if (blockType == BlockType.EQUATIONS) {

      // declaring expression exists by construction from symbol table creator
      // there no shape without declaring expression
      return getVectorizedVariable(getDeclaringExpression().get(), getEnclosingScope()).isPresent();
    }
    else {
      return getVectorParameter().isPresent();
    }

  }

  public boolean isPredefined() {
    return this.blockType == BlockType.PREDEFINED;
  }


  public Optional<String> getVectorParameter() {
    if (blockType != BlockType.EQUATIONS) {
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

  public boolean isFunctionalShape() {
    return variableType == VariableType.SHAPE && !getName().contains("'");
  }

  public boolean isState() {
    return blockType == BlockType.STATE;
  }

  public boolean isInInitialValues() {
    return blockType == BlockType.INITIAL_VALUES;
  }

  public void markShape() {
    this.variableType = VariableType.SHAPE;
  }

  public boolean isShape() {
    return variableType == VariableType.SHAPE;
  }

  public boolean isInternal() {
    return blockType == BlockType.INTERNALS;
  }

  public boolean isInEquation() {
    return blockType == BlockType.EQUATIONS;
  }

  @SuppressWarnings({"unused"}) // used in templates
  public boolean containsSumCall() {
    return declaringExpression != null && OdeTransformer.containsSumFunctionCall(declaringExpression);
  }

  public boolean isParameter() {
    return blockType == BlockType.PARAMETERS;
  }

  public void setFunction(boolean isAlias) {
    this.isFunction = isAlias;
  }

  public boolean isFunction() {
    return isFunction;
  }

  public BlockType getBlockType() {
    return blockType;
  }

  @SuppressWarnings({"unused"}) // used in templates
  public boolean hasSetter() {
    checkState(getAstNode().isPresent(), "Symbol table must set the AST node.");
    checkArgument(getAstNode().get().getEnclosingScope().isPresent(), "Run symboltable creator.");

    return isSetterPresent(getName(), getType().getName(), getAstNode().get().getEnclosingScope().get());
  }

  @SuppressWarnings({"unused"}) // used in templates
  public boolean hasGetter() {
    checkState(getAstNode().isPresent(), "Symbol table must set the AST node.");
    checkArgument(getAstNode().get().getEnclosingScope().isPresent(), "Run symboltable creator.");

    return isGetterPresent(getName(), getType().getName(), getAstNode().get().getEnclosingScope().get());
  }

  @SuppressWarnings({"unused"}) // used in templates
  public Optional<String> getComment() {
    if(getAstNode().isPresent() && getAstNode().get() instanceof ASTDeclaration) {
      final ASTDeclaration astDeclaration = (ASTDeclaration) getAstNode().get();
      return Optional.of(astDeclaration.getDocString());
    }
    else {
      return Optional.empty();
    }

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

  public enum VariableType {
    SHAPE,
    VARIABLE,
    BUFFER,
    EQUATION
  }

  public enum BlockType {
    STATE,
    PARAMETERS,
    INTERNALS,
    INITIAL_VALUES,
    EQUATIONS,
    LOCAL,
    OUTPUT,
    INPUT,
    PREDEFINED
  }

}
