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

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Creates a artifact scope, build the symbol table and adds predifined types.
 *
 * @author plotnikov
 */
public class NESTMLScopeCreator extends ScopeCreatorBase {
  private GlobalScope globalScope;
  private final ModelPath modelPath;
  private final ResolverConfiguration resolverConfiguration;
  private final NESTMLLanguage nestmlLanguages;

  public GlobalScope getGlobalScope() {
    return globalScope;
  }

  public   NESTMLScopeCreator(
      final Path modelPathAsString) {

    modelPath = new ModelPath(modelPathAsString);

    nestmlLanguages = new NESTMLLanguage();

    resolverConfiguration = new ResolverConfiguration();
    resolverConfiguration.addTopScopeResolvers(nestmlLanguages.getResolvers());

  }

  public Scope runSymbolTableCreator(final ASTNESTMLCompilationUnit compilationUnit) {
    globalScope = new GlobalScope(
        modelPath,
        nestmlLanguages,
        resolverConfiguration);
    addPredefinedFunctions(globalScope);
    final NESTMLSymbolTableCreator symbolTableCreator = new CommonNESTMLSymbolTableCreator(
        resolverConfiguration,
        globalScope);

    return symbolTableCreator.createFromAST(compilationUnit);
  }

}
