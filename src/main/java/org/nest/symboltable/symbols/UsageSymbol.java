/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;
import de.monticore.symboltable.SymbolKind;

/**
 * Represents the usage of a component in an neuron.
 *
 * @author plotnikov
 */
public class UsageSymbol extends CommonSymbol {
  public final static UsageSymbolKind KIND = new UsageSymbolKind();
  private final String usageName;
  private final NeuronSymbol referencedSymbol;

  public UsageSymbol(final String usageName, final NeuronSymbol referencedSymbol) {
    super(usageName, KIND);
    this.referencedSymbol = referencedSymbol;
    this.usageName = usageName;
  }

  @Override
  public String toString() {
    return "UsageSymbol(" + getFullName() + ")";
  }

  public NeuronSymbol getReferencedSymbol() {
    return referencedSymbol;
  }

  public static class UsageSymbolKind implements SymbolKind {

    protected UsageSymbolKind() {
    }

  }

}
