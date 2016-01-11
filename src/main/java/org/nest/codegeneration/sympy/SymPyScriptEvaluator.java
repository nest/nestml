/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

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
public class SymPyScriptEvaluator {

  private final static String LOG_NAME = SymPyScriptEvaluator.class.getName();

  public final static String ODE_TYPE = "solverType.property";
  public final static String P30_FILE = "P30.mat";
  public static final String CONSTANT_TERM = "constantTerm.mat";
  public final static String PSC_INITIAL_VALUE_FILE = "pscInitialValue.mat";
  public final static String STATE_VECTOR_FILE = "state.vector.mat";
  public final static String UPDATE_STEP_FILE = "update.step.mat";



  public boolean execute(final Path generatedScript) {

    try {
      info("Begins long running SymPy script evaluation...", LOG_NAME);
      final Process res = Runtime.getRuntime().exec(
          "python " + generatedScript.getFileName(),
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
