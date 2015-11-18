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

  private GlobalScope globalScope;

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

  final ModelPath modelPath;
  final ResolverConfiguration resolverConfiguration;
  final NESTMLLanguage nestmlLanguages;

  public   NESTMLScopeCreator(
      final String modelPathAsString,
      final PredefinedTypesFactory typesFactory) {
    super(typesFactory);

    modelPath = new ModelPath(Paths.get(modelPathAsString));

    nestmlLanguages = new NESTMLLanguage(typesFactory);

    resolverConfiguration = new ResolverConfiguration();
    resolverConfiguration.addTopScopeResolvers(nestmlLanguages.getResolvers());

    // TODO is only for a successufl test there
    globalScope = new GlobalScope(
        modelPath,
        nestmlLanguages.getModelLoader(),
        resolverConfiguration);
    addPredefinedTypes(globalScope);
    addPredefinedFunctions(globalScope);
    addPredefinedVariables(globalScope);
    // END
  }

  public Scope runSymbolTableCreator(final ASTNESTMLCompilationUnit compilationUnit) {
    globalScope = new GlobalScope(
        modelPath,
        nestmlLanguages.getModelLoader(),
        resolverConfiguration);
    addPredefinedTypes(globalScope);
    addPredefinedFunctions(globalScope);
    addPredefinedVariables(globalScope);
    final NESTMLSymbolTableCreator symbolTableCreator = new CommonNESTMLSymbolTableCreator(
        resolverConfiguration,
        globalScope,
        typesFactory);

    return symbolTableCreator.createFromAST(compilationUnit);
  }




}
