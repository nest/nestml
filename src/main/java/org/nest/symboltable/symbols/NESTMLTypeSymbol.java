/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import com.google.common.collect.Lists;
import de.monticore.symboltable.CommonSymbol;

import java.util.Collection;
import java.util.Optional;

import static java.util.Optional.empty;

/**
 * Represents an entire neuron or component. E.g. for
 *
 * {@code neuron A: end}
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLTypeSymbol extends CommonSymbol {

  public final static NESTMLTypeSymbolKind KIND = new NESTMLTypeSymbolKind();

  private final static Collection<NESTMLMethodSymbol> builtInMethods = Lists.newArrayList();

  private final Type type;

  public NESTMLTypeSymbol(final String name, final Type type) {
    super(name, KIND);
    this.type = type;
  }

  public Type getType() {
    return type;
  }

  public void addBuiltInMethod(final NESTMLMethodSymbol builtInMethod) {
    builtInMethods.add(builtInMethod);
  }

  public Optional<NESTMLMethodSymbol> getBuiltInMethod(final String methodName) {
    // TODO signature must be considered
    return builtInMethods.stream().filter(method -> method.getName().equals(methodName)).findFirst();
  }

  @Override
  public String toString() {
    return "NESTMLTypeSymbol(" + getFullName() + "," + type + ")";
  }

  public enum Type { UNIT, PRIMITIVE}
}
