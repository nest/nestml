/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import de.monticore.symboltable.CommonSymbol;

/**
 * Represents the entire neuron, e.g. iaf_neuron.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLUsageSymbol extends CommonSymbol {
  public final static NESTMLUsageSymbolKind KIND = new NESTMLUsageSymbolKind();
  private final String usageName;
  private final NESTMLNeuronSymbol referencedSymbol;

  public NESTMLUsageSymbol(final String usageName, final NESTMLNeuronSymbol referencedSymbol) {
    super(usageName, KIND);
    this.referencedSymbol = referencedSymbol;
    this.usageName = usageName;
  }

  @Override
  public String toString() {
    return "NESTMLUsageSymbol(" + getFullName() + ")";
  }

  public NESTMLNeuronSymbol getReferencedSymbol() {
    return referencedSymbol;
  }
}
