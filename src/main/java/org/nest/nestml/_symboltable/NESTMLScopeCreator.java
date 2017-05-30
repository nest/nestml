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
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.ScopeCreatorBase;
import org.nest.units._visitor.ODEPostProcessingVisitor;
import org.nest.utils.LogHelper;

import java.nio.file.Path;

/**
 * Creates a artifact scope, build the symbol table and adds predifined types.
 *
 * @author plotnikov
 */
public class NESTMLScopeCreator extends ScopeCreatorBase {
  private final static String LOG_NAME = "NESTML_" + NESTMLScopeCreator.class.getName();
  private GlobalScope globalScope;
  private final ModelPath modelPath;
  private final ResolverConfiguration resolverConfiguration;
  private final NESTMLLanguage nestmlLanguage;

  public GlobalScope getGlobalScope() {
    return globalScope;
  }

  public NESTMLScopeCreator(final Path modelPathAsString) {

    modelPath = new ModelPath(modelPathAsString);

    nestmlLanguage = new NESTMLLanguage();

    resolverConfiguration = new ResolverConfiguration();
    resolverConfiguration.addDefaultFilters(nestmlLanguage.getResolvers());
  }

  public Scope runSymbolTableCreator(final ASTNESTMLCompilationUnit compilationUnit) {
    globalScope = new GlobalScope(modelPath, nestmlLanguage, resolverConfiguration);

    final NESTMLSymbolTableCreator symbolTableCreator = new NESTMLSymbolTableCreator(
        resolverConfiguration,
        globalScope);

    Scope result = symbolTableCreator.createFromAST(compilationUnit);

    /* TODO DO I NEED this check?
    final List<Finding> findings = compilationUnit.getNeurons()
        .stream()
        .map(nestmlCoCosManager::checkThatVariablesDefinedOnce)
        .flatMap(Collection::stream)
        .collect(Collectors.toList());
     */

    if (LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()).isEmpty() &&
        LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()).isEmpty()) {
      final ODEPostProcessingVisitor odePostProcessingVisitor = new ODEPostProcessingVisitor();
      compilationUnit.accept(odePostProcessingVisitor);
    }
    else {
      Log.error(LOG_NAME + ": The symboltable is built incorrectly, skip the step of processing ODEs.");
    }

    return result;
  }

}
