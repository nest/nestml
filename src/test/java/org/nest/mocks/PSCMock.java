/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.mocks;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.codegeneration.sympy.SymPyScriptEvaluator;
import org.nest.nestml._ast.ASTNeuron;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Provides a mock for the psc_alpha neuron defined with an ode.
 *
 * @author plotnikov
 */
public class PSCMock extends ODEProcessor {
  private final static String MOCK_RESOURCE_PATH = "src/test/resources/codegeneration/sympy/psc/";

  @Override
  protected ASTNeuron handleNeuronWithODE(final ASTNeuron root, final Path outputBase) {
    Log.trace("Uses PSC mock", this.getClass().getName());
    return getExactSolutionTransformer().replaceODEWithSymPySolution(
            root,
            Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.P30_FILE),
            Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE),
            Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.STATE_VARIABLES_FILE),
            Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.STATE_VECTOR_UPDATE_FILE),
            Paths.get(MOCK_RESOURCE_PATH, SymPyScriptEvaluator.UPDATE_STEP_FILE));
  }

}