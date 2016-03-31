/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolKind;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

/**
 * TODO
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since TODO
 */
public class PredefinedVariablesFilter extends CommonResolvingFilter<VariableSymbol> {
  public PredefinedVariablesFilter(
      final Class<VariableSymbol> symbolClass,
      final SymbolKind targetKind) {
    super(targetKind);
  }

  @Override
  public Optional<Symbol> filter(
      final ResolvingInfo resolvingInfo,
      final String name,
      final List<Symbol> symbols) {
    final Optional<VariableSymbol> predefinedVariable = PredefinedVariables.getVariableIfExists(name);
    if (predefinedVariable.isPresent()) {
      return Optional.of(predefinedVariable.get());
    }
    else {
      return Optional.empty();
    }

  }

}
