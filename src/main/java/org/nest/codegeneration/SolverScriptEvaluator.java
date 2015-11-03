/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.se_rwth.commons.logging.Log;

import java.io.*;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

import static de.se_rwth.commons.logging.Log.debug;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.info;

/**
 * The class is responsible for the execution of the python code which
 * was generated from the neuron model.
 *
 * @author plotnikov
 */
public class SolverScriptEvaluator {

  final private static String LOG_NAME = SolverScriptEvaluator.class.getName();

  public boolean execute(final Path generatedScript) {

    try {
      info("Begins long running SymPy script evaluation...", LOG_NAME);
      final Process res = Runtime.getRuntime().exec(
          "python iaf_neuron_ode_neuronSolver.py",
          new String[0],
          new File(generatedScript.getParent().toString()));
      res.waitFor();
      info("Successfully evaluated the SymPy script", LOG_NAME);

      // reports standard output
      getListFromStream(res.getInputStream())
          .forEach(outputLine -> debug(outputLine, LOG_NAME));

      // reports errors
      getListFromStream(res.getErrorStream()).forEach(Log::error);

      if (getListFromStream(res.getErrorStream()).size() > 0) {
        return false;
      }

      // Read generated matrix entries
    }
    catch (IOException | InterruptedException e) {
      error("Cannot evaluate the SymPy script: " + generatedScript.toString(), e);
      return false;
    }

    return true;
  }


  private List<String> getListFromStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }
}
