/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import org.junit.Test;
import org.nest.base.GenerationTestBase;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.codegeneration.sympy.SymPyScriptEvaluator;
import org.nest.mocks.PSCMock;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 */
public class NESTCodeGeneratorTest extends GenerationTestBase {

  private final PSCMock pscMock = new PSCMock();
  private final String PSC_MODEL = "src/test/resources/codegeneration/iaf_neuron_ode.nestml";
  private final String COND_MODEL_EXPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha.nestml";
  private final String COND_MODEL_IMPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha_implicit.nestml";

  public NESTCodeGeneratorTest() {

  }

  @Test
  public void testPSCModel() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL);
    scopeCreator.runSymbolTableCreator(root);
    final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator, pscMock);
    generator.analyseAndGenerate(root, Paths.get("target"));

  }



}
