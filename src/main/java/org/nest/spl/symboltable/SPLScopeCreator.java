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
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.nio.file.Paths;

/**
 * TODO: Write me!
 *
 * @author plotnikov
 * @since 0.0.2
 */
public class SPLScopeCreator extends ScopeCreatorBase {

  private static final String LOGGER_NAME = SPLScopeCreator.class.getName();

  private final GlobalScope globalScope;

  final SPLSymbolTableCreator symbolTableCreator;

  public GlobalScope getGlobalScope() {
    return globalScope;
  }

  public SPLScopeCreator(
      final String modelPathAsString,
      final PredefinedTypesFactory typesFactory) {
    super(typesFactory);

    final ModelPath modelPath = new ModelPath(Paths.get(modelPathAsString));

    final SPLLanguage splLanguage = new SPLLanguage(typesFactory);

    final ResolverConfiguration resolverConfiguration = new ResolverConfiguration();
    resolverConfiguration.addTopScopeResolvers(splLanguage.getResolvers());

    globalScope = new GlobalScope(
        modelPath,
        splLanguage,
        resolverConfiguration);

    addPredefinedTypes(globalScope);
    addPredefinedFunctions(globalScope);
    addPredefinedVariables(globalScope);

    symbolTableCreator = new CommonSPLSymbolTableCreator(
        resolverConfiguration, globalScope, typesFactory);

  }

  public Scope runSymbolTableCreator(final ASTSPLFile compilationUnit) {
    return symbolTableCreator.createFromAST(compilationUnit);
  }

  @Override
  public String getLogger() {
    return LOGGER_NAME;
  }

}
