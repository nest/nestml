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
import org.nest.nestml._symboltable.PredefinedTypesFilter;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl.symboltable.CommonSPLSymbolTableCreator;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

/**
 * Frontend for the Simple Programming Language (SPL)
 *
 * @author plotnikov
 */
public class SPLLanguage extends org.nest.spl._symboltable.SPLLanguageTOP {

  public static final String FILE_ENDING = "simple";

  /**
   * {@inheritDoc}
   */
  public SPLLanguage() {
    super("SPL Language", FILE_ENDING); // TODO what is the top level in this case?
  }

  /**
   * {@inheritDoc}
   */
  @Override
  public Optional<CommonSPLSymbolTableCreator> getSymbolTableCreator(ResolverConfiguration resolverConfiguration, MutableScope enclosingScope) {
    return Optional.of(new CommonSPLSymbolTableCreator(resolverConfiguration, enclosingScope));
  }

  @Override protected void initResolvingFilters() {
    super.initResolvingFilters();
    addResolver(new PredefinedTypesFilter());
    addResolver(CommonResolvingFilter.create(VariableSymbol.KIND));
    addResolver(CommonResolvingFilter.create(MethodSymbol.KIND));
  }

  @Override protected ModelingLanguageModelLoader<ASTSPLFile> provideModelLoader() {
    return new org.nest.spl.symboltable.SPLModelLoader(this);
  }
}
