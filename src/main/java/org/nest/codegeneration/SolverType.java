/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.se_rwth.commons.logging.Log;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Determine the type of the supported solver.
 *
 * @author plotnikov
 */
public enum SolverType {
  EXACT, NUMERIC, NONE;

  public static SolverType fromFile(final Path solverTypeFile) {
    try {
      final List<String> lines = Files.readAllLines(solverTypeFile);
      checkState(lines.size() == 1);
      final String computedSolverType = lines.get(0);
      final Optional<SolverType> type = Arrays.stream(values())
          .filter(enumCandidate -> enumCandidate.toString().equalsIgnoreCase(computedSolverType))
          .findFirst();

      return type.orElse(NONE);
    }
    catch (IOException e) {
      Log.error("Cannot open the property file: " + solverTypeFile.toString(), e);
      return NONE;
    }

  }

}
