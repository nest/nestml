/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.io.paths.ModelPath;
import de.monticore.symboltable.GlobalScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.ScopeCreatorBase;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.nio.file.Paths;

/**
 * Creates a artifact scope, build the symbol table and adds predifined types.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLScopeCreator extends ScopeCreatorBase {
  final static String LOG_NAME = NESTMLScopeCreator.class.getName();

  private final NESTMLSymbolTableCreator symbolTableCreator;

  @Override
  public String getLogger() {
    return LOG_NAME;
  }

  public PredefinedTypesFactory getTypesFactory() {
    return typesFactory;
  }

  public GlobalScope getGlobalScope() {
    return globalScope;
  }

  final GlobalScope globalScope;

  public   NESTMLScopeCreator(
      final String modelPathAsString,
      final PredefinedTypesFactory typesFactory) {
    super(typesFactory);

    final ModelPath modelPath = new ModelPath(Paths.get(modelPathAsString));

    final NESTMLLanguage nestmlLanguages = new NESTMLLanguage(typesFactory);

    final ResolverConfiguration resolverConfiguration = new ResolverConfiguration();
    resolverConfiguration.addTopScopeResolvers(nestmlLanguages.getResolvers());

    globalScope = new GlobalScope(modelPath, nestmlLanguages.getModelLoader(), resolverConfiguration);
    addPredefinedTypes(globalScope);
    addPredefinedFunctions(globalScope);
    addPredefinedVariables(globalScope);

    symbolTableCreator = new CommonNESTMLSymbolTableCreator(resolverConfiguration, globalScope, typesFactory);

  }

  public Scope runSymbolTableCreator(final ASTNESTMLCompilationUnit compilationUnit) {
    return symbolTableCreator.createFromAST(compilationUnit);
  }

}
