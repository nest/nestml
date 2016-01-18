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
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 */
public class NESTCodeGeneratorTest extends GenerationTestBase {
  private final static String MOCK_RESOURCE_PATH = "src/test/resources/codegeneration/sympy/psc/";
  private final PSCMock pscMock = new PSCMock();
  private final String PSC_MODEL = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";
  private final String COND_MODEL_EXPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha_module.nestml";
  private final String COND_MODEL_IMPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha_implicit_module.nestml";

  public NESTCodeGeneratorTest() {

  }
  class PSCMock extends ODEProcessor {
    @Override
    protected ASTNESTMLCompilationUnit handleNeuronWithODE(
        ASTNESTMLCompilationUnit root, Path outputBase) {
      final ASTNESTMLCompilationUnit transformedModel = getExactSolutionTransformer()
          .replaceODEWithSymPySolution(
              root,
              Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.P30_FILE),
              Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE),
              Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.STATE_VECTOR_FILE),
              Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.UPDATE_STEP_FILE));

      return transformedModel;
    }
  }



  @Test
  public void testPSCModel() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL);
    scopeCreator.runSymbolTableCreator(root);
    final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator, pscMock);
    generator.analyseAndGenerate(root, Paths.get("target"));

  }

}
