package org.nest.nestml._symboltable;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;

import java.io.IOException;
import java.util.Optional;

/**
 * Created by user on 3/26/15.
 */
public class NESTMLRootCreator {
  /**
   * Parses the model and returns ast.
   * @throws java.io.IOException
   */
  public static Optional<ASTNESTMLCompilationUnit> getAstRoot(String modelPath) {
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    try {
      return p.parse(modelPath);
    }
    catch (IOException e) {
      Log.error("Cannot parse the model: " + modelPath, e);

    }
    return Optional.empty();
  }
}
