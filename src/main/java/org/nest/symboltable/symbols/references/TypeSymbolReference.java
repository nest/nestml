/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols.references;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.references.CommonSymbolReference;
import de.monticore.symboltable.references.SymbolReference;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * Represents a reference to a nestml type.
 *
 * @author plotnikov
 */
public class TypeSymbolReference extends TypeSymbol implements
    SymbolReference<TypeSymbol> {

  private final SymbolReference<TypeSymbol> typeReference;

  public TypeSymbolReference(final String name, Type type, Scope definingScopeOfReference) {
    super(name, type);
    typeReference = new CommonSymbolReference<>(name, TypeSymbol.KIND, definingScopeOfReference);
  }

  @Override
  public TypeSymbol getReferencedSymbol() {
    return typeReference.getReferencedSymbol();
  }

  @Override
  public boolean existsReferencedSymbol() {
    return typeReference.existsReferencedSymbol();
  }

  @Override public boolean isReferencedSymbolLoaded() {
    return typeReference.isReferencedSymbolLoaded();
  }

  @Override
  public String getName() {
    return typeReference.getReferencedSymbol().getName();
  }

  @Override
  public Type getType() {
    return typeReference.getReferencedSymbol().getType();
  }


}
