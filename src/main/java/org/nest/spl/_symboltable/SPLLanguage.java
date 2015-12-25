/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._symboltable;

import de.monticore.modelloader.ModelingLanguageModelLoader;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl.symboltable.*;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

/**
 * Frontend for the Simple Programming Language (SPL)
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class SPLLanguage extends org.nest.spl._symboltable.SPLLanguageTOP {

  public static final String FILE_ENDING = "simple";

  final PredefinedTypesFactory typesFactory;

  /**
   * {@inheritDoc}
   */
  public SPLLanguage(final PredefinedTypesFactory typesFactory) {
    super("SPL Language", FILE_ENDING); // TODO what is the top level in this case?
    this.typesFactory = typesFactory;
  }

  /**
   * {@inheritDoc}
   */
  @Override
  public Optional<CommonSPLSymbolTableCreator> getSymbolTableCreator(ResolverConfiguration resolverConfiguration, MutableScope enclosingScope) {
    return Optional.of(new CommonSPLSymbolTableCreator(resolverConfiguration, enclosingScope, typesFactory));
  }

  @Override protected void initResolvingFilters() {
    super.initResolvingFilters();
    addResolver(CommonResolvingFilter.create(TypeSymbol.class, TypeSymbol.KIND));
    addResolver(CommonResolvingFilter.create(VariableSymbol.class, VariableSymbol.KIND));
    addResolver(CommonResolvingFilter.create(MethodSymbol.class, MethodSymbol.KIND));
  }

  @Override protected ModelingLanguageModelLoader<ASTSPLFile> provideModelLoader() {
    return new org.nest.spl.symboltable.SPLModelLoader(this);
  }
}
