/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import de.monticore.symboltable.ArtifactScope;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import static de.se_rwth.commons.logging.Log.error;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._symboltable.SPLLanguage;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Strings.isNullOrEmpty;
import static de.se_rwth.commons.logging.Log.info;
import static de.se_rwth.commons.logging.Log.warn;

/**
 * Creates symbol table for the {@code SPLLanguage} from the parsed model.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class SPLModelLoader extends org.nest.spl._symboltable.SPLModelLoader {

  public static final String LOGGER_NAME = SPLModelLoader.class.getName();

  public SPLModelLoader(final SPLLanguage modelingLanguage) {
    super(modelingLanguage);
  }

  @Override
  protected void createSymbolTableFromAST(
      final ASTSPLFile ast,
      final String modelName,
      final MutableScope enclosingScope,
      final ResolverConfiguration resolverConfiguration) {

    final Optional<CommonSPLSymbolTableCreator> symbolTableCreator
        = getModelingLanguage().getSymbolTableCreator(resolverConfiguration, enclosingScope);

    if (symbolTableCreator.isPresent()) {
      final String msg = "Start creation of symbol table for model \"" + modelName + "\".";
      info(msg, LOGGER_NAME);
      final Scope scope = symbolTableCreator.get().createFromAST(ast);

      if (!(scope instanceof ArtifactScope)) {
        warn("Top scope of model " + modelName + " is expected to be a compilation scope, but"
            + " is scope \"" + scope.getName() + "\"");
      }

      info(LOGGER_NAME, "Created symbol table for model \"" + modelName + "\".");
    }
    else {
      warn("No symbol created, because '" + getModelingLanguage().getName()
          + "' does not define a symbol table creator.");
    }

  }
  public SPLLanguage getModelingLanguage() {
    return super.getModelingLanguage();
  }
}
