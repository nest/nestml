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
import org.nest.codegeneration.helpers.AliasInverter;
import org.nest.commons._ast.ASTBLOCK_CLOSE;
import org.nest.commons._ast.ASTBLOCK_OPEN;
import org.nest.commons._ast.ASTExpr;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.ode._ast.ASTShape;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.*;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.helpers.AliasInverter.isInvertableExpression;
import static org.nest.codegeneration.helpers.AliasInverter.isRelativeExpression;
import static org.nest.utils.AstUtils.printComments;

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

  public List<ASTAliasDecl> getStateDeclarations() {
    final Optional<ASTBodyElement> stateBlock = getStateBlock();
    final List<ASTAliasDecl> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( ((ASTVar_Block) block).getAliasDecls()));
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

  public List<ASTAliasDecl> getParameterDeclarations() {
    final Optional<ASTBodyElement> stateBlock = getParameterBlock();
    final List<ASTAliasDecl> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( ((ASTVar_Block) block).getAliasDecls()));
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

  public List<ASTAliasDecl> getInternalDeclarations() {
    final Optional<ASTBodyElement> stateBlock = getInternalBlock();
    final List<ASTAliasDecl> result = Lists.newArrayList();
    stateBlock.ifPresent(block -> result.addAll( ((ASTVar_Block) block).getAliasDecls()));
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
    if (block.isPresent()) {
      return printComments(block.get());
    }
    else {
      return "";
    }
  }

  // STATE variables handling
  public List<VariableSymbol> getStateSymbols() {
    return this.getEnclosingScope().get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(stateSymbol -> (VariableSymbol) stateSymbol)
        .filter(VariableSymbol::isState)
        .collect(toList());

  }

  public List<VariableSymbol> getStateAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isState), getEnclosingScope().get())
        .stream()
        .filter(VariableSymbol::isAlias)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getStateNonAliasSymbols() {
    final Collection<VariableSymbol> variableSymbols = getEnclosingScope().get().resolveLocally(VariableSymbol.KIND);
    return variableSymbols
        .stream()
        .filter(VariableSymbol::isState)
        .filter(variableSymbol -> !variableSymbol.isAlias())
        .collect(Collectors.toList());
  }

  // Parameter variable handling
  public List<VariableSymbol> getParameterSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isParameters ), getEnclosingScope().get());
  }

  public List<VariableSymbol> getParameterAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isParameters ), getEnclosingScope().get())
        .stream()
        .filter(VariableSymbol::isAlias)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getParameterNonAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isParameters ), getEnclosingScope().get())
        .stream()
        .filter(variable -> !variable.isAlias())
        .collect(Collectors.toList());
  }

  // Internal variables handling
  public List<VariableSymbol> getInternalSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isInternals), getEnclosingScope().get());
  }

  public List<VariableSymbol> getInternalAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isInternals), getEnclosingScope().get())
        .stream()
        .filter(VariableSymbol::isAlias)
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getInternalNonAliasSymbols() {
    return getVariableSymbols(getDeclarationsFromBlock(ASTVar_Block::isInternals), getEnclosingScope().get())
        .stream()
        .filter(variable -> !variable.isAlias())
        .collect(Collectors.toList());
  }

  private List<ASTAliasDecl> getDeclarationsFromBlock(final Predicate<ASTVar_Block> predicate) {
    final List<ASTAliasDecl> result = Lists.newArrayList();

    this.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;
      if (predicate.test(block)) {
        result.addAll(block.getAliasDecls());
      }
    });

    return result;
  }

  private List<VariableSymbol> getVariableSymbols(
      final List<ASTAliasDecl> aliasDeclarations,
      final Scope scope) {
    return aliasDeclarations.stream()
        .flatMap(alias -> alias.getDeclaration().getVars().stream()) // get all variables form the declaration
        .map(variable -> VariableSymbol.resolve(variable, scope))
        .collect(toList());
  }


  public List<ASTExpr> getParameterInvariants() {
    return getParameterDeclarations().stream()
        .filter(param -> param.getInvariant().isPresent())
        .map(param -> param.getInvariant().get()) // ensured by the filter function
        .collect(toList());
  }

  public void addToInternalBlock(final ASTAliasDecl astAliasDecl) {
    this.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isInternals()) {
        block.getAliasDecls().add(astAliasDecl);
      }

    });

  }

  public void addToStateBlock(final ASTAliasDecl astAliasDecl) {
    this.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isState()) {
        block.getAliasDecls().add(astAliasDecl);
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

  /**
   * TODO It is very NEST related. Factor it out
   * @return
   */
  public List<VariableSymbol> getAllOffsetVariables() {
    final List<VariableSymbol> aliases = Lists.newArrayList();
    aliases.addAll(getParameterAliasSymbols());
    aliases.addAll(getStateAliasSymbols());

    final List<VariableSymbol> invertableAliases = aliases.stream()
        .filter(variable -> isInvertableExpression(variable.getDeclaringExpression().get()) ||
               (variable.isParameters () && isRelativeExpression(variable.getDeclaringExpression().get())))
        .collect(Collectors.toList());

    // Use sets to filter double variables, e.g. a variable that is used twice on the right side
    final Set<VariableSymbol> offsets = invertableAliases.stream()
        .map(alias -> AliasInverter.offsetVariable(alias.getDeclaringExpression().get()))
        .collect(Collectors.toSet());

    return Lists.newArrayList(offsets);
  }

  /**
   * TODO It is very NEST related. Factor it out
   * @return
   */
  public List<VariableSymbol> getAllRelativeParameters() {
    return  getParameterAliasSymbols().stream()
        .filter(variable -> isRelativeExpression(variable.getDeclaringExpression().get()))
        .collect(Collectors.toList());
  }

  public Optional<ASTOdeDeclaration> getODEBlock() {
    final Optional<ASTBodyElement> odeBlock = bodyElements
        .stream()
        .filter(astBodyElement -> astBodyElement instanceof ASTEquations)
        .findAny();
    if (odeBlock.isPresent()) {
      return Optional.of(((ASTEquations) odeBlock.get()).getOdeDeclaration()); // checked by the filter conditions
    }
    else {
      return Optional.empty();
    }

  }

  public List<VariableSymbol> getODEAliases() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(variable -> (VariableSymbol) variable)
        .filter(variable -> variable.isAlias() && variable.isInEquation())
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

  public List<VariableSymbol> getSameTypeBuffer() {
    return enclosingScope.get().resolveLocally(VariableSymbol.KIND)
        .stream()
        .map(inputBuffer -> (VariableSymbol) inputBuffer)
        .filter(VariableSymbol::isSpikeBuffer)
        .filter(VariableSymbol::isInhAndExc)
        .collect(Collectors.toList());
  }

}
