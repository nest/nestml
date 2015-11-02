package org.nest.ode;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.*;
import de.monticore.symboltable.modifiers.AccessModifier;
import de.monticore.symboltable.resolving.ResolvingFilter;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Created by user on 20.05.15.
 */
public class ScopeMock implements Scope {

  @Override public Optional<String> getName() {
    return Optional.of("TestScope");
  }

  @Override public Optional<? extends Scope> getEnclosingScope() {
    return null;
  }

  @Override public List<? extends Scope> getSubScopes() {
    return null;
  }

  @Override public <T extends Symbol> Optional<T> resolve(String s, SymbolKind symbolKind) {
    return null;
  }

  @Override public <T extends Symbol> Optional<T> resolve(String s, SymbolKind symbolKind,
      AccessModifier accessModifier) {
    return null;
  }

  @Override public <T extends Symbol> Collection<T> resolveMany(String name, SymbolKind kind) {
    return null;
  }

  @Override public <T extends Symbol> Optional<T> resolveLocally(String s, SymbolKind symbolKind) {

    return null;
  }

  @Override public <T extends Symbol> List<T> resolveLocally(SymbolKind symbolKind) {
    return null;
  }

  @Override public Optional<? extends Symbol> resolve(SymbolPredicate symbolPredicate) {
    return null;
  }

  @Override public List<Symbol> getSymbols() {
    return null;
  }

  @Override public int getSymbolsSize() {
    return 0;
  }

  @Override public boolean isShadowingScope() {
    return false;
  }

  @Override public Optional<? extends ScopeSpanningSymbol> getSpanningSymbol() {
    return null;
  }

  @Override public Set<ResolvingFilter<? extends Symbol>> getResolvingFilters() {
    return null;
  }

  @Override public Optional<? extends ASTNode> getAstNode() {
    return null;
  }
}
