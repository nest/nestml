/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import de.monticore.io.paths.ModelPath;
import de.monticore.symboltable.GlobalScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.Scope;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._symboltable.SPLLanguage;
import org.nest.symboltable.ScopeCreatorBase;

import java.nio.file.Paths;

/**
 * TODO: Write me!
 *
 */
public class SPLScopeCreator extends ScopeCreatorBase {

  private GlobalScope globalScope;
  private final ModelPath modelPath;
  private final ResolverConfiguration resolverConfiguration;
  final SPLLanguage splLanguage;

  public GlobalScope getGlobalScope() {
    return globalScope;
  }

  public SPLScopeCreator(final String modelPathAsString) {
    modelPath = new ModelPath(Paths.get(modelPathAsString));

    splLanguage = new SPLLanguage();
    resolverConfiguration = new ResolverConfiguration();
    resolverConfiguration.addDefaultFilters(splLanguage.getResolvers());
  }

  public Scope runSymbolTableCreator(final ASTSPLFile compilationUnit) {
    globalScope = new GlobalScope(
        modelPath,
        splLanguage,
        resolverConfiguration);
    addPredefinedFunctions(globalScope);
    addPredefinedTypes(globalScope);
    addPredefinedVariables(globalScope);

    final CommonSPLSymbolTableCreator symbolTableCreator = new CommonSPLSymbolTableCreator(
        resolverConfiguration,
        globalScope);

    return symbolTableCreator.createFromAST(compilationUnit);
  }

}
