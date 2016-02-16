/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import de.monticore.symboltable.CommonScopeSpanningSymbol;
import de.monticore.symboltable.SymbolKind;

/**
 * TODO
 *
 * @author plotnikov
 */
public class NeuronScope extends CommonScopeSpanningSymbol {
  public NeuronScope(String name, SymbolKind kind) {
    super(name, kind);
  }

}
