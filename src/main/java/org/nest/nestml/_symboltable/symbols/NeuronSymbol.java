/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable.symbols;

import com.google.common.collect.Lists;
import de.monticore.ast.Comment;
import de.monticore.symboltable.CommonScopeSpanningSymbol;
import de.monticore.symboltable.SymbolKind;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static java.util.stream.Collectors.toList;

/**
 * Represents the entire neuron or component, e.g. iaf_neuron.
 *
 * @author plotnikov
 */
public class NeuronSymbol extends CommonScopeSpanningSymbol {

  public final static NeuronSymbolKind KIND = new NeuronSymbolKind();

  private final Type type;

  public NeuronSymbol(final String name, final Type type) {
    super(name, KIND);
    this.type = type;
  }

  public Type getType() {
    return type;
  }

  @Override
  public String toString() {
    return "NeuronSymbol(" + getFullName() + "," + type + ")";
  }

  @SuppressWarnings("unused") // it is used within freemarker templates
  public List<VariableSymbol> getStateVariables() {
    return getSpannedScope().<VariableSymbol> resolveLocally(VariableSymbol.KIND)
        .stream()
        .filter(VariableSymbol::isState)
        .collect(toList());
  }

  public Optional<VariableSymbol> getVariableByName(String variableName) {
    return getSpannedScope().resolveLocally(variableName, VariableSymbol.KIND);
  }


  @SuppressWarnings("unused") // it is used within freemarker templates
  public List<VariableSymbol> getCurrentBuffers() {
    final Collection<VariableSymbol> variableSymbols
        = getSpannedScope().resolveLocally(VariableSymbol.KIND);
    return variableSymbols.stream()
        .filter(VariableSymbol::isCurrentBuffer)
        .collect(toList());
  }

  @SuppressWarnings("unused") // it is used within freemarker templates
  public List<VariableSymbol> getSpikeBuffers() {
    final Collection<VariableSymbol> variableSymbols = getSpannedScope().resolveLocally(VariableSymbol.KIND);
    return variableSymbols.stream()
        .filter(VariableSymbol::isSpikeBuffer)
        .collect(toList());
  }

  @SuppressWarnings("unused") // it is used within freemarker templates
  public boolean isMultisynapseSpikes() {
    return getSpikeBuffers()
        .stream()
        .anyMatch(VariableSymbol::isVector);
  }

  public MethodSymbol getUpdateBlock() {
    // the existence is checked by a context condition
    final Optional<MethodSymbol> methodSymbol = getSpannedScope().resolveLocally("dynamics", MethodSymbol.KIND);
    return methodSymbol.get();
  }

  @SuppressWarnings("unused") // it is used in the NeuronHeader.ftl generator template
  public List<String> getDocStrings() {
    final List<String> result = Lists.newArrayList();

    if(getAstNode().isPresent()) {
      result.addAll(escapeAndPrintComment(getAstNode().get().get_PreComments()));
      result.addAll(escapeAndPrintComment(getAstNode().get().get_PostComments()));

    }
    return result;
  }

  /**
   * Replaces the multiline comment characters and returns it as a string of strings.
   */
  private List<String> escapeAndPrintComment(final List<Comment> comments) {
    return comments.stream()
        .map(comment -> comment.getText().replace("/*", "").replace("*/", ""))
        .flatMap(comment -> Arrays.stream(comment.split("\\n")))
        .map(String::trim)
        .collect(toList());
  }

  /**
   * The same symbol is used for neurons and components. To  distinguish between them, this enum is
   * used.
   */
  public enum Type { NEURON, COMPONENT }

  static private class NeuronSymbolKind implements SymbolKind {

    NeuronSymbolKind() {
    }

  }

}
