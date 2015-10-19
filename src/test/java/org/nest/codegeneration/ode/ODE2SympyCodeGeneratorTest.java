/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.ode;

import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.Names;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.*;
import java.nio.file.Path;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.nestml._parser.NESTMLParserFactory.*;

/**
 * TODO
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class ODE2SympyCodeGeneratorTest {
  private static final String TEST_MODEL_PATH = "src/test/resources/";

  public static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";

  private static final String OUTPUT_FOLDER = "target";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void generateSympyScript() throws IOException {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p =
        createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);

    assertTrue(root.isPresent());
    final File outputFolder = new File(OUTPUT_FOLDER);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = ODE2SympyCodeGenerator.generateSympyODEAnalyzer(
        glex,
        root.get(),
        root.get().getNeurons().get(0),
        outputFolder);

    assertTrue(generatedScript.isPresent());
  }

  @Ignore
  @Test
  public void executePythonScript() throws IOException {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);

    assertTrue(root.isPresent());
    final File outputFolder = new File(OUTPUT_FOLDER);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = ODE2SympyCodeGenerator.generateSympyODEAnalyzer(
        glex,
        root.get(),
        root.get().getNeurons().get(0),
        outputFolder);

    assertTrue(generatedScript.isPresent());
    final Process res = Runtime.getRuntime().exec(
        "python iaf_neuron_ode_neuronSolver.py",
        new String[0],
        new File(generatedScript.get().getParent().toString()));

    printInputStream("input: ", res.getInputStream());
    printInputStream("error: ", res.getErrorStream());

  }

  private void printInputStream(final String prefix, final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    String line;
    while ((line = in.readLine()) != null) {
      System.out.println(prefix + ": " + line);
    }
  }

  private GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}
