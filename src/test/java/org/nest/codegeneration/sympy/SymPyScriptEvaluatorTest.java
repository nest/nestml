/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Ignore;
import org.junit.Test;
import org.nest.DisableFailQuickMixin;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.*;
import java.nio.file.Path;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Test evaluation of the solver script. Depends on successful script generation.
 *
 * @author plonikov
 */
public class SymPyScriptEvaluatorTest extends DisableFailQuickMixin {
  private static final String TEST_MODEL_PATH = "src/test/resources/";

  public static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iiaf_cond_alpha_neuron.nestml";

  private static final String OUTPUT_FOLDER = "target";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Ignore // takes long time, therefore, enabled only for the manual execution
  @Test
  public void generateAndExecuteSympyScript() throws IOException {
    final NESTMLCompilationUnitMCParser p = createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);

    assertTrue(root.isPresent());
    final File outputFolder = new File(OUTPUT_FOLDER);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = SymPyScriptGenerator.generateSympyODEAnalyzer(
        root.get(),
        root.get().getNeurons().get(0),
        outputFolder);

    assertTrue(generatedScript.isPresent());
    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();

    assertTrue(evaluator.execute(generatedScript.get()));
  }

}
