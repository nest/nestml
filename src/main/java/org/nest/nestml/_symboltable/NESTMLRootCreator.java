package org.nest.nestml._symboltable;

import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;

import java.io.IOException;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Created by user on 3/26/15.
 */
public class NESTMLRootCreator {
  final static NESTMLParser parser = new NESTMLParser();
  /**
   * Parses the model and returns ast.
   * @throws java.io.IOException
   */
  public static Optional<ASTNESTMLCompilationUnit> getAstRoot(String modelPath) {
    try {
      return parser.parse(modelPath);
    }
    catch (IOException e) {
      error("Cannot parse the model: " + modelPath, e);

    }
    return Optional.empty();
  }
}
