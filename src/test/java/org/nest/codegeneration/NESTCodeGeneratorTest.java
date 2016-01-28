/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import org.junit.Test;
import org.nest.base.GenerationTestBase;
import org.nest.mocks.PSCMock;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.nio.file.Path;
import java.nio.file.Paths;

import static com.google.common.collect.Lists.newArrayList;

/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 */
public class NESTCodeGeneratorTest extends GenerationTestBase {

  public static final Path OUTPUT_DIRECTORY = Paths.get("target", "build");

  private final PSCMock pscMock = new PSCMock();
  private final String PSC_MODEL = "src/test/resources/codegeneration/iaf_neuron_ode.nestml";
  private final String COND_MODEL_EXPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha.nestml";
  private final String COND_MODEL_IMPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha_implicit.nestml";


  @Test
  public void testPSCModelWithOde() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL);
    scopeCreator.runSymbolTableCreator(root);
    final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator, pscMock);
    generator.analyseAndGenerate(root, OUTPUT_DIRECTORY);
    generator.generateNESTModuleCode(newArrayList(root), "codegeneration", OUTPUT_DIRECTORY);
  }

}
