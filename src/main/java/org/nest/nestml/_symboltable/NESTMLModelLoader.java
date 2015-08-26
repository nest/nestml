/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.modelloader.ModelingLanguageModelLoader;
import de.monticore.symboltable.ArtifactScope;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import static de.se_rwth.commons.logging.Log.debug;

/**
 * Creates symbol table for the {@code NESTMLLanguage} from the parsed model.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLModelLoader extends ModelingLanguageModelLoader<ASTNESTMLCompilationUnit> {

  public NESTMLModelLoader(NESTMLLanguage language) {
    super(language);
  }

  @Override
  protected void createSymbolTableFromAST(
      final ASTNESTMLCompilationUnit ast,
      final String modelName,
      final MutableScope enclosingScope,
      final ResolverConfiguration resolverConfiguration) {
    final NESTMLSymbolTableCreator symbolTableCreator = getModelingLanguage().getSymbolTableCreator
        (resolverConfiguration, enclosingScope).orElse(null);

    if (symbolTableCreator != null) {
      debug("Start creation of symbol table for model \"" + modelName + "\".",
          NESTMLModelLoader.class.getSimpleName());
      final Scope scope = symbolTableCreator.createFromAST(ast);

      if (!(scope instanceof ArtifactScope)) {
        Log.warn("Top scope of model " + modelName + " is expected to be a compilation scope, but"
            + " is scope \"" + scope.getName() + "\"");
      }

      debug("Created symbol table for model \"" + modelName + "\".",
          NESTMLModelLoader.class.getSimpleName());
    }
    else {
      Log.warn("No symbol created, because '" + getModelingLanguage().getName()
          + "' does not define a symbol table creator.");
    }

  }

  @Override
  public NESTMLLanguage getModelingLanguage() {
    return (NESTMLLanguage) super.getModelingLanguage();
  }
}
