/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import org.nest.codegeneration.sympy.AstCreator;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toList;

/**
 * Provides convenient  functions to statically type interfaces astnodes resulting from the Body-grammar
 * production.
 *
 * @author plotnikov
 */
public class ASTNeuron extends ASTNeuronTOP {

  public ASTNeuron() {
    // this constructor is used in the generated code and must be provided
  }

  public ASTNeuron(
      final String name,
      final ASTBLOCK_OPEN bLOCK_open,
      final List<String> nEWLINEs,
      final List<ASTBlockWithVariables> blockWithVariabless,
      final List<ASTUpdateBlock> updateBlocks,
      final List<ASTEquationsBlock> equationss,
      final List<ASTInputBlock> inputs,
      final List<ASTOutputBlock> outputs,
      final List<ASTFunction> functions,
      final ASTBLOCK_CLOSE bLOCK_close) {
    super(name, bLOCK_open, nEWLINEs, blockWithVariabless, updateBlocks, equationss, inputs, outputs, functions, bLOCK_close);
  }

  public Optional<ASTUpdateBlock> getUpdateBlock() {
    return this.getUpdateBlocks().stream().findFirst();
  }

  /**
   * It is used in the dynamics functions
   * @return
   */
  public String printDynamicsComment() {
    return printBlockComment(getUpdateBlock());
  }

  public Optional<ASTBlockWithVariables> getStateBlock() {
    return this.getBlockWithVariabless()
        .stream()
        .filter(ASTBlockWithVariables::isState)
        .findFirst(); // there is at most one
  }

  public List<ASTDeclaration> getStateDeclarations() {
    final Optional<ASTBlockWithVariables> stateBlock = getStateBlock();
    final List<ASTDeclaration> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( block.getDeclarations()));
    return result;
  }

  public String printStateComment() {
    return printBlockComment(getStateBlock());
  }

  public Optional<ASTBlockWithVariables> getParameterBlock() {
    return this.getBlockWithVariabless()
        .stream()
        .filter(ASTBlockWithVariables::isParameters)
        .findFirst(); // there is at most one
  }

  public List<ASTDeclaration> getParameterDeclarations() {
    final Optional<ASTBlockWithVariables> stateBlock = getParameterBlock();
    final List<ASTDeclaration> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll(block.getDeclarations()));
    return result;
  }

  public String printParameterComment() {
    return printBlockComment(getParameterBlock());
  }

  public Optional<ASTBlockWithVariables> getInternalBlock() {
    return this.getBlockWithVariabless()
        .stream()
        .filter(ASTBlockWithVariables::isInternals)
        .findFirst(); // there is at most one
  }

  public List<ASTDeclaration> getInternalDeclarations() {
    final Optional<ASTBlockWithVariables> stateBlock = getInternalBlock();
    final List<ASTDeclaration> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll(block.getDeclarations()));
    return result;
  }

  public String printInternalComment() {
    return printBlockComment(getInternalBlock());
  }

  public List<ASTEquation> getEquations() {
    final Optional<ASTEquationsBlock> equations = findEquationsBlock();
    if (equations.isPresent()) {
      return equations.get().getEquations();
    }
    else {
      return Lists.newArrayList();
    }
  }

  public List<ASTShape> getShapes() {
    final Optional<ASTEquationsBlock> equations = findEquationsBlock();
    if (equations.isPresent()) {
      return equations.get().getShapes();
    }
    else {
      return Lists.newArrayList();
    }
  }

  public Optional<ASTEquationsBlock> findEquationsBlock() {
    return this.getEquationsBlocks()
        .stream()
        .findFirst();

  }

  private String printBlockComment(final Optional<? extends ASTNode> block) {
    return block.map(AstUtils::printComments).orElse("");
  }

  // STATE variables handling
  public List<VariableSymbol> getStateSymbols() {
    return this.getSpannedScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(stateSymbol -> (VariableSymbol) stateSymbol)
        .filter(VariableSymbol::isState)
        .collect(toList());

  }

  public List<ASTDeclaration> getInitialValuesDeclarations() {
    Optional<ASTBlockWithVariables> initialValuesBlock = getInitialValuesBlock();
    final List<ASTDeclaration> initialValuesDeclarations = Lists.newArrayList();
    initialValuesBlock.ifPresent(block -> initialValuesDeclarations.addAll(block.getDeclarations()));
    return initialValuesDeclarations;
  }

  public Optional<ASTBlockWithVariables> getInitialValuesBlock() {
    return getBlockWithVariabless()
          .stream()
          .filter(ASTBlockWithVariables::isInitial_values)
          .findFirst();
  }

  public List<VariableSymbol> getInitialValuesSymbols() {
    return this.getSpannedScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(variable -> (VariableSymbol) variable)
        .filter(VariableSymbol::isInInitialValues)
        .collect(toList());
  }

  public List<VariableSymbol> getNonFunctionInitialValuesSymbols() {
    return this.getSpannedScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(variable -> (VariableSymbol) variable)
        .filter(VariableSymbol::isInInitialValues)
        .filter(variableSymbol -> !variableSymbol.isFunction())
        .collect(toList());
  }

  public List<VariableSymbol> getFunctionInitialValuesSymbols() {
    return this.getSpannedScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(variable -> (VariableSymbol) variable)
        .filter(VariableSymbol::isInInitialValues)
        .filter(VariableSymbol::isFunction)
        .collect(toList());
  }


  public List<VariableSymbol> getStateAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isState), getSpannedScope().get())
        .stream()
        .filter(VariableSymbol::isFunction)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getStateNonAliasSymbols() {
    final Collection<VariableSymbol> variableSymbols = getSpannedScope().get().resolveLocally(VariableSymbol.KIND);
    return variableSymbols
        .stream()
        .filter(VariableSymbol::isState)
        .filter(variableSymbol -> !variableSymbol.isFunction())
        .collect(Collectors.toList());
  }

  // Parameter variable handling
  public List<VariableSymbol> getParameterSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isParameters ), getSpannedScope().get());
  }

  public List<VariableSymbol> getParameterAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isParameters ), getSpannedScope().get())
        .stream()
        .filter(VariableSymbol::isFunction)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getParameterNonAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isParameters ), getSpannedScope().get())
        .stream()
        .filter(variable -> !variable.isFunction())
        .collect(Collectors.toList());
  }

  // Internal variables handling
  public List<VariableSymbol> getInternalSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isInternals), getSpannedScope().get());
  }

  public List<VariableSymbol> getInternalAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isInternals), getSpannedScope().get())
        .stream()
        .filter(VariableSymbol::isFunction)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getInternalNonAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTBlockWithVariables::isInternals), getSpannedScope().get())
        .stream()
        .filter(variable -> !variable.isFunction())
        .collect(Collectors.toList());
  }

  private List<ASTDeclaration> getDeclarationsFromBlock(final Predicate<ASTBlockWithVariables> blockSelector) {
    final List<ASTDeclaration> result = Lists.newArrayList();

    this.getBlockWithVariabless().stream()
        .filter(blockSelector)
        .forEach(block -> result.addAll(block.getDeclarations()));

    return result;
  }

  private List<VariableSymbol> getVariableSymbols(
      final List<ASTDeclaration> aliasDeclarations,
      final Scope scope) {
    return aliasDeclarations.stream()
        .flatMap(declaration -> declaration.getVars().stream()) // get all variables form the declaration
        .map(variable -> VariableSymbol.resolve(variable.toString(), scope))
        .collect(toList());
  }


  public List<ASTExpr> getParameterInvariants() {
    return getParameterDeclarations().stream()
        .filter(param -> param.getInvariant().isPresent())
        .map(param -> param.getInvariant().get()) // ensured by the filter function
        .collect(toList());
  }

  public void addToInternalBlock(final ASTDeclaration astDeclaration) {
    if (!this.getInternalBlock().isPresent()) {
      final ASTBlockWithVariables internalBlock = AstCreator.createInternalBlock();
      getBlockWithVariabless().add(internalBlock);
    }

    this.getBlockWithVariabless().forEach(block -> {
      if (block.isInternals()) {
        block.getDeclarations().add(astDeclaration);
      }

    });

  }

  public void addToInitialValuesBlock(ASTDeclaration astDeclaration) {
    if (!this.getInternalBlock().isPresent()) {
      final ASTBlockWithVariables internalBlock = AstCreator.createInitialValuesBlock();
      getBlockWithVariabless().add(internalBlock);
    }

    this.getBlockWithVariabless().forEach(block -> {
      if (block.isInitial_values()) {
        block.getDeclarations().add(astDeclaration);
      }

    });
  }

  public void addToStateBlock(final ASTDeclaration astDeclaration) {
    if (!this.getInternalBlock().isPresent()) {
      final ASTBlockWithVariables stateBlock = AstCreator.createStateBlock();
      getBlockWithVariabless().add(stateBlock);
    }

    this.getBlockWithVariabless().forEach(block -> {
      if (block.isState()) {
        block.getDeclarations().add(astDeclaration);
      }

    });

  }

  public List<ASTInputLine> getInputLines() {
    List<ASTInputLine> result = Lists.newArrayList();

    for (final ASTInputBlock inputBlock : this.getInputBlocks()) {
      result.addAll(inputBlock.getInputLines());
    }

    return result;
  }

  public void removeEquationsBlock() {
    this.setEquationsBlocks(Lists.newArrayList());
  }

  public List<VariableSymbol> getODEAliases() {
    return spannedScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(variable -> (VariableSymbol) variable)
        .filter(variable -> variable.isFunction() && variable.isInEquation())
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getInputBuffers() {
    return spannedScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(inputBuffer -> inputBuffer.isSpikeBuffer() || inputBuffer.isCurrentBuffer())
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getSpikeBuffers() {
    return spannedScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isSpikeBuffer)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getCurrentBuffers() {
    return spannedScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isCurrentBuffer)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getMultipleReceptors() {
    return spannedScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isSpikeBuffer)
        .filter(VariableSymbol::isInhAndExc)
        .collect(Collectors.toList());
  }

  public boolean isArrayBuffer() {
    return spannedScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isBuffer)
        .anyMatch(VariableSymbol::isVector);
  }

  public void removeShapes() {
    this.findEquationsBlock().get().getShapes().clear();
  }

}
