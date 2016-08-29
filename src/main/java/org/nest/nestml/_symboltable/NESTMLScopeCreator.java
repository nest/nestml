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
import de.se_rwth.commons.logging.Finding;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.ScopeCreatorBase;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.units._visitor.UnitsSIVisitor;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

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

    final NESTMLSymbolTableCreator symbolTableCreator = new NESTMLSymbolTableCreator(
        resolverConfiguration,
        globalScope);

    return symbolTableCreator.createFromAST(compilationUnit);
  }

}
