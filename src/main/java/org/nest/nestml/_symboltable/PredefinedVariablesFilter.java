/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.nestml._symboltable.predefined.PredefinedVariables;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;

/**
 * Returns a predefined variable (e.g. 't') if one exists.
 *
 * @author plotnikov
 */
public class PredefinedVariablesFilter extends CommonResolvingFilter<VariableSymbol> {
  public PredefinedVariablesFilter() {
    super(VariableSymbol.KIND);
  }


  public Optional<Symbol> filter(ResolvingInfo resolvingInfo, String name, Map<String, Collection<Symbol>> symbols) {
    final Optional<VariableSymbol> predefinedVariable = PredefinedVariables.getVariableIfExists(name);
    if (predefinedVariable.isPresent()) {
      return Optional.of(predefinedVariable.get());
    }
    else {
      return Optional.empty();
    }

  }

}
