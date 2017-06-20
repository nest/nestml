/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.ArtifactScope;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolvingConfiguration;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import static de.se_rwth.commons.logging.Log.trace;

/**
 * Creates symbol table for the {@code NESTMLLanguage} from the parsed model.
 *
 * @author plotnikov
 */
public class NESTMLModelLoader extends NESTMLModelLoaderTOP {

  public NESTMLModelLoader(NESTMLLanguage language) {
    super(language);
  }

  @Override
  protected void createSymbolTableFromAST(
      final ASTNESTMLCompilationUnit ast,
      final String modelName,
      final MutableScope enclosingScope,
      final ResolvingConfiguration resolvingConfiguration) {
    final String NO_CREATOR = "Register symbol table creator in the language.";
    final NESTMLSymbolTableCreator symbolTableCreator = getModelingLanguage()
        .getSymbolTableCreator(resolvingConfiguration, enclosingScope)
        .orElseThrow(() -> new RuntimeException(NO_CREATOR));

    ast.setArtifactName(Names.getSimpleName(modelName));

    if (symbolTableCreator != null) {
      trace("Start creation of symbol table for model \"" + modelName + "\".",
          NESTMLModelLoader.class.getSimpleName());
      final Scope scope = symbolTableCreator.createFromAST(ast);

      if (!(scope instanceof ArtifactScope)) {
        Log.trace("Top scope of model " + modelName + " is expected to be a compilation scope, but"
            + " is scope \"" + scope.getName() + "\"", NESTMLModelLoader.class.getSimpleName());
      }

      trace("Created symbol table for model \"" + modelName + "\".",
          NESTMLModelLoader.class.getSimpleName());
    }
    else {
      Log.trace("No symbol created, because '" + getModelingLanguage().getName()
          + "' does not define a symbol table creator.", NESTMLModelLoader.class.getSimpleName());
    }

  }

}
