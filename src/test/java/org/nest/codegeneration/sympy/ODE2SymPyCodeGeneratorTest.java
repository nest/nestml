/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.se_rwth.commons.logging.Log;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.*;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static org.junit.Assert.assertTrue;
import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Test the overall script generation and evaluation of the generated scripts
 *
 * @author plotnikov
 */
public class ODE2SymPyCodeGeneratorTest {
  private static final String TEST_MODEL_PATH = "src/test/resources/";

  public static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";

  private static final String OUTPUT_FOLDER = "target";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void generateSympyScript() throws IOException {
    final NESTMLCompilationUnitMCParser p =
        createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);

    assertTrue(root.isPresent());
    final File outputFolder = new File(OUTPUT_FOLDER);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = ODE2SymPyCodeGenerator.generateSympyODEAnalyzer(
        root.get(),
        root.get().getNeurons().get(0),
        outputFolder);

    assertTrue(generatedScript.isPresent());
  }

  @Ignore
  @Test
  public void generateAndExecuteSympyScript() throws IOException {
    final NESTMLCompilationUnitMCParser p = createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);

    assertTrue(root.isPresent());
    final File outputFolder = new File(OUTPUT_FOLDER);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = ODE2SymPyCodeGenerator.generateSympyODEAnalyzer(
        root.get(),
        root.get().getNeurons().get(0),
        outputFolder);

    assertTrue(generatedScript.isPresent());
    Log.info("Begins long running script evaluation...", "TODO Logger");
    final Process res = Runtime.getRuntime().exec(
        "python iaf_neuron_ode_neuronSolver.py",
        new String[0],
        new File(generatedScript.get().getParent().toString()));
    Log.info("Successfully evaluated the symby script", "TODO Logger");

    // TODO should be extracted into error handling
    printInputStream(res.getInputStream())
        .forEach(outputLine -> System.out.printf("Output: " + outputLine));
    printInputStream(res.getErrorStream())
        .forEach(errorLine -> System.out.println("Error: " + errorLine));
    // Read generated matrix entries
  }

  private List<String> printInputStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }


}
