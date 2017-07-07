/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.base.Charsets;
import com.google.common.collect.Lists;
import com.google.common.io.Resources;
import org.nest.nestml._ast.ASTOdeDeclaration;
import org.nest.nestml._ast.ASTShape;
import org.nest.reporting.Reporter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * The class is responsible for the execution of the PYTHON_INTERPRETER code which
 * was generated from the neuron model.
 * was generated from the neuron model.
 *
 * @author plotnikov
 */
class SymPySolver {
  private final static Reporter reporter = Reporter.get();

  private final static String PYTHON_INTERPRETER = "python";
  private static final String SHAPES_SCRIPT = "shapes.py";
  private static final String SHAPES_SOURCE = "org/nest/sympy/shapes.py";

  private static final String PROP_MATRIX_SCRIPT = "prop_matrix.py";
  private static final String PROP_MATRIX_SOURCE = "org/nest/sympy/prop_matrix.py";

  private static final String ODE_ANALYZER_SCRIPT = "OdeAnalyzer.py";
  private static final String ODE_ANALYZER_SOURCE = "org/nest/sympy/OdeAnalyzer.py";

  SolverOutput solveOdeWithShapes(final ASTOdeDeclaration astOdeDeclaration, final Path output) {
    return executeSolver(new SolverInput(astOdeDeclaration), output);
  }

  SolverOutput solveShapes(final List<ASTShape> shapes, final Path output) {
    return executeSolver(new SolverInput(shapes), output);
  }

  private SolverOutput executeSolver(final SolverInput solverInput, final Path output) {
    try {
      reporter.reportProgress("Start long running SymPy script evaluation...");

      copySolverFramework(output);
      long start = System.nanoTime();
      final List<String> commands = Lists.newArrayList();

      commands.add(PYTHON_INTERPRETER);
      commands.add(ODE_ANALYZER_SCRIPT);
      commands.add(solverInput.toJSON());

      final ProcessBuilder processBuilder = new ProcessBuilder(
          PYTHON_INTERPRETER,
          ODE_ANALYZER_SCRIPT,
          solverInput.toJSON()).directory(output.toFile()).command(commands);

      final Process res = processBuilder.start();
      res.waitFor();
      long end = System.nanoTime();

      // reports standard output
      getStreamAsListOfStrings(res.getInputStream()).forEach(reporter::reportProgress);
      // reports errors
      getStreamAsListOfStrings(res.getErrorStream()).forEach(reporter::reportProgress);

      long elapsedTime = end - start;
      final String msg = "Successfully evaluated the SymPy script. Elapsed time: "
          + (double)elapsedTime / 1000000000.0 +  " [s]";
      reporter.reportProgress(msg);

      if (getStreamAsListOfStrings(res.getErrorStream()).size() > 0) {
        getStreamAsListOfStrings(res.getErrorStream())
            .forEach(error -> reporter.reportProgress(error, Reporter.Level.ERROR));

        reporter.reportProgress("Cannot evaluate the SymPy solver scripts.", Reporter.Level.ERROR);
        return SolverOutput.getErrorResult();
      }

      return SolverOutput.fromJSON(Paths.get(output.toString(), SolverOutput.RESULT_FILE_NAME));
    }
    catch (IOException | InterruptedException e) {
      reporter.reportProgress("Cannot evaluate the SymPy solver scripts.", Reporter.Level.ERROR);
      return SolverOutput.getErrorResult();
    }

  }

  private void copySolverFramework(final Path output) {
    try {
      final URL shapesPyUrl = getClass().getClassLoader().getResource(SHAPES_SOURCE);
      checkNotNull(shapesPyUrl, "Cannot read the solver script: " + SHAPES_SCRIPT);
      final String shapesPy = Resources.toString(shapesPyUrl, Charsets.UTF_8);
      Files.write(Paths.get(output.toString(), SHAPES_SCRIPT), shapesPy.getBytes());

      final URL propMatrixUrl = getClass().getClassLoader().getResource(PROP_MATRIX_SOURCE);
      checkNotNull(propMatrixUrl, "Cannot read the solver script: " + PROP_MATRIX_SCRIPT);
      final String propMatrixPy = Resources.toString(propMatrixUrl, Charsets.UTF_8);
      Files.write(Paths.get(output.toString(), PROP_MATRIX_SCRIPT), propMatrixPy.getBytes());

      final URL odeAnalyzerUrl = getClass().getClassLoader().getResource(ODE_ANALYZER_SOURCE);
      checkNotNull(odeAnalyzerUrl, "Cannot read the solver script: " + ODE_ANALYZER_SCRIPT);
      final String odeAnalyzerPy = Resources.toString(odeAnalyzerUrl, Charsets.UTF_8);
      Files.write(Paths.get(output.toString(), ODE_ANALYZER_SCRIPT), odeAnalyzerPy.getBytes());

    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private List<String> getStreamAsListOfStrings(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }

}
