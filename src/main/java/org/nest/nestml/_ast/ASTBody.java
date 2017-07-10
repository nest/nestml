/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import org.nest.codegeneration.sympy.AstCreator;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.ArrayList;
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
@SuppressWarnings({"unused"}) // function are used in freemarker templates
public class ASTBody extends ASTBodyTOP {

  public ASTBody() {
    // this constructor is used in the generated code and must be provided
  }

  public ASTBody(
      final ASTBLOCK_OPEN bLOCK_open,
      final List<String> nEWLINEs,
      final List<ASTBodyElement> bodyElements,
      final ASTBLOCK_CLOSE bLOCK_close) {
    super(bLOCK_open, nEWLINEs, bodyElements, bLOCK_close);
  }

  // Retrieves model structure blocks
  public List<ASTFunction> getFunctions() {
    List<ASTFunction> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTFunction)
        .map(be -> (ASTFunction) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTDynamics> getDynamics() {
    List<ASTDynamics> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTDynamics)
        .map(be -> (ASTDynamics) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public Optional<ASTDynamics> getDynamicsBlock() {
    return this.getBodyElements().stream()
        .filter(be -> be instanceof ASTDynamics)
        .map(be -> (ASTDynamics) be)
        .findFirst();
  }

  public String printDynamicsComment() {
    return printBlockComment(getDynamicsBlock());
  }

  public Optional<ASTBodyElement> getStateBlock() {
    return this.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isState())
        .findFirst(); // there is at most one
  }

  public List<ASTDeclaration> getStateDeclarations() {
    final Optional<ASTBodyElement> stateBlock = getStateBlock();
    final List<ASTDeclaration> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( ((ASTVar_Block) block).getDeclarations()));
    return result;
  }

  public String printStateComment() {
    return printBlockComment(getStateBlock());
  }
  public Optional<ASTBodyElement> getParameterBlock() {
    return this.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isParameters ())
        .findFirst(); // there is at most one
  }

  public List<ASTDeclaration> getParameterDeclarations() {
    final Optional<ASTBodyElement> stateBlock = getParameterBlock();
    final List<ASTDeclaration> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( ((ASTVar_Block) block).getDeclarations()));
    return result;
  }

  public String printParameterComment() {
    return printBlockComment(getParameterBlock());
  }

  public Optional<ASTBodyElement> getInternalBlock() {
    return this.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isInternals())
        .findFirst(); // there is at most one
  }

  public List<ASTDeclaration> getInternalDeclarations() {
    final Optional<ASTBodyElement> stateBlock = getInternalBlock();
    final List<ASTDeclaration> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( ((ASTVar_Block) block).getDeclarations()));
    return result;
  }

  public String printInternalComment() {
    return printBlockComment(getInternalBlock());
  }

  public List<ASTEquation> getEquations() {
    final Optional<ASTEquations> equations = findEquationsBlock();
    if (equations.isPresent()) {
      return equations.get().getOdeDeclaration().getODEs();
    }
    else {
      return Lists.newArrayList();
    }
  }

  public List<ASTShape> getShapes() {
    final Optional<ASTEquations> equations = findEquationsBlock();
    if (equations.isPresent()) {
      return equations.get().getOdeDeclaration().getShapes();
    }
    else {
      return Lists.newArrayList();
    }
  }

  public List<VariableSymbol> variablesDefinedByODE() {
    return getStateSymbols()
        .stream()
        .filter(VariableSymbol::definedByODE)
        .collect(toList());
  }

  private Optional<ASTEquations> findEquationsBlock() {
    final Optional<ASTBodyElement> equations = this.getBodyElements()
        .stream()
        .filter(be -> be instanceof ASTEquations)
        .findFirst();
    if (equations.isPresent()) {
      // only ASTEquations are filtered
      return Optional.of((ASTEquations) equations.get());
    }
    else {
      return Optional.empty();
    }
  }

  private String printBlockComment(final Optional<? extends ASTNode> block) {
    return block.map(AstUtils::printComments).orElse("");
  }

  // STATE variables handling
  public List<VariableSymbol> getStateSymbols() {
    return this.getEnclosingScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(stateSymbol -> (VariableSymbol) stateSymbol)
        .filter(VariableSymbol::isState)
        .collect(toList());

  }

  public List<VariableSymbol> getOdeDefinedSymbols() {
    return this.getEnclosingScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(stateSymbol -> (VariableSymbol) stateSymbol)
        .filter(VariableSymbol::isState)
        .filter(VariableSymbol::definedByODE)
        .collect(toList());

  }

  public List<VariableSymbol> getStateSymbolsWithoutOde() {
    return this.getEnclosingScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(stateSymbol -> (VariableSymbol) stateSymbol)
        .filter(VariableSymbol::isState)
        .filter(variableSymbol -> !variableSymbol.definedByODE())
        .collect(toList());

  }

  public List<VariableSymbol> getStateAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isState), getEnclosingScope().get())
        .stream()
        .filter(VariableSymbol::isFunction)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getStateNonAliasSymbols() {
    final Collection<VariableSymbol> variableSymbols = getEnclosingScope().get().resolveLocally(VariableSymbol.KIND);
    return variableSymbols
        .stream()
        .filter(VariableSymbol::isState)
        .filter(variableSymbol -> !variableSymbol.isFunction())
        .collect(Collectors.toList());
  }

  // Parameter variable handling
  public List<VariableSymbol> getParameterSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isParameters ), getEnclosingScope().get());
  }

  public List<VariableSymbol> getParameterAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isParameters ), getEnclosingScope().get())
        .stream()
        .filter(VariableSymbol::isFunction)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getParameterNonAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isParameters ), getEnclosingScope().get())
        .stream()
        .filter(variable -> !variable.isFunction())
        .collect(Collectors.toList());
  }

  // Internal variables handling
  public List<VariableSymbol> getInternalSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isInternals), getEnclosingScope().get());
  }

  public List<VariableSymbol> getInternalAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isInternals), getEnclosingScope().get())
        .stream()
        .filter(VariableSymbol::isFunction)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getInternalNonAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isInternals), getEnclosingScope().get())
        .stream()
        .filter(variable -> !variable.isFunction())
        .collect(Collectors.toList());
  }

  private List<ASTDeclaration> getDeclarationsFromBlock(final Predicate<ASTVar_Block> predicate) {
    final List<ASTDeclaration> result = Lists.newArrayList();

    this.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;
      if (predicate.test(block)) {
        result.addAll(block.getDeclarations());
      }
    });

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
      final ASTVar_Block internalBlock = AstCreator.createInternalBlock();
      getBodyElements().add(internalBlock);
    }

    this.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isInternals()) {
        block.getDeclarations().add(astDeclaration);
      }

    });

  }

  public void addToStateBlock(final ASTDeclaration ASTDeclaration) {
    this.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isState()) {
        block.getDeclarations().add(ASTDeclaration);
      }

    });

  }

  private Optional<ASTBodyElement> findDynamics() {
    return this.getBodyElements().stream()
          .filter(be -> be instanceof ASTDynamics)
          .findFirst();
  }

  public List<ASTInputLine> getInputLines() {
    List<ASTInputLine> result = new ArrayList<ASTInputLine>();

    for (ASTBodyElement be : this.getBodyElements()) {
      if (be instanceof ASTInput) {
        ASTInput in = (ASTInput) be;
        for (ASTInputLine inline : in.getInputLines()) {
          result.add(inline);
        }
      }
    }

    return ImmutableList.copyOf(result);
  }

  public List<ASTOutput> getOutputs() {
    final List<ASTOutput> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTOutput)
        .map(be -> (ASTOutput) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public Optional<ASTOdeDeclaration> getOdeBlock() {
    final Optional<ASTBodyElement> odeBlock = bodyElements
        .stream()
        .filter(astBodyElement -> astBodyElement instanceof ASTEquations)
        .findAny();
    // checked by the filter conditions
    return odeBlock.map(astBodyElement -> ((ASTEquations) astBodyElement).getOdeDeclaration());

  }

  public void removeOdeBlock() {
    final Optional<ASTBodyElement> odeBlock = bodyElements
        .stream()
        .filter(astBodyElement -> astBodyElement instanceof ASTEquations)
        .findAny();

    odeBlock.ifPresent(astBodyElement -> bodyElements.remove(astBodyElement));
  }

  public List<VariableSymbol> getODEAliases() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(variable -> (VariableSymbol) variable)
        .filter(variable -> variable.isFunction() && variable.isInEquation())
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getInputBuffers() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(inputBuffer -> inputBuffer.isSpikeBuffer() || inputBuffer.isCurrentBuffer())
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getSpikeBuffers() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isSpikeBuffer)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getCurrentBuffers() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isCurrentBuffer)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getMultipleReceptors() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isSpikeBuffer)
        .filter(VariableSymbol::isInhAndExc)
        .collect(Collectors.toList());
  }

  public boolean isArrayBuffer() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isBuffer)
        .anyMatch(VariableSymbol::isVector);
  }

}
