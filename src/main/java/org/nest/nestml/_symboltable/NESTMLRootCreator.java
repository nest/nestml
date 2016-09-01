/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Creates symbol table for the {@code NESTMLLanguage} from the parsed model.
 *
 * @author plotnikov
 */
public class NESTMLRootCreator {

  /**
   * Parses the model and returns ast.
   * @throws java.io.IOException
   */
  public static Optional<ASTNESTMLCompilationUnit> getAstRoot(
      final String modelFile,
      final Path modelPath) {
    final NESTMLParser parser = new NESTMLParser(modelPath);
    try {
      return parser.parse(modelFile);
    }
    catch (IOException e) {
      error("Cannot parse the model: " + modelFile, e);
    }
    return Optional.empty();
  }
}
