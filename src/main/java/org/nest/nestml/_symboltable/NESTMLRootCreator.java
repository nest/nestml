package org.nest.nestml._symboltable;

import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Created by user on 3/26/15.
 */
public class NESTMLRootCreator {

  /**
   * Parses the model and returns ast.
   * @throws java.io.IOException
   */
  public static Optional<ASTNESTMLCompilationUnit> getAstRoot(final String modelFile, final String modelPath) {
    final NESTMLParser parser = new NESTMLParser(Paths.get(modelPath));
    try {
      return parser.parse(modelFile);
    }
    catch (IOException e) {
      error("Cannot parse the model: " + modelFile, e);
    }
    return Optional.empty();
  }
}
