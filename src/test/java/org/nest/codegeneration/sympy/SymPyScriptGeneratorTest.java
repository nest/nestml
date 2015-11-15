/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.Names.getPathFromPackage;
import static de.se_rwth.commons.Names.getQualifiedName;
import static org.junit.Assert.assertTrue;
import static org.nest.codegeneration.sympy.SymPyScriptGenerator.generateSympyODEAnalyzer;
import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Tests that the solver script is generated from an ODE based model.
 *
 * @author plotnikov
 */
public class SymPyScriptGeneratorTest {
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
    final String fullName = getQualifiedName(root.get().getPackageName().getParts());
    final File outputFolder = new File(Paths.get(OUTPUT_FOLDER, getPathFromPackage(fullName)).toString());

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = generateSympyODEAnalyzer(
        root.get(),
        root.get().getNeurons().get(0),
        outputFolder);

    assertTrue(generatedScript.isPresent());
  }


}
