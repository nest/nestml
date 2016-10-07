/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.mocks;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.sympy.ImplicitFormTransformer;
import org.nest.codegeneration.sympy.OdeProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Provides a mock for the cond_alpha neuron defined with an ode.
 *
 * @author plotnikov
 */
public class CondMock extends OdeProcessor {
  private final static String MOCK_RESOURCE_PATH = "src/test/resources/codegeneration/sympy/cond/";

  @Override
  protected ASTNeuron handleNeuronWithODE(final ASTNeuron root, ASTNESTMLCompilationUnit artifactRoot, final Path outputBase) {
    Log.trace("Uses COND mock", this.getClass().getName());
    return getImplicitFormTransformer().transformToImplicitForm(
            root,
            Paths.get(MOCK_RESOURCE_PATH, ImplicitFormTransformer.PSC_INITIAL_VALUE_FILE),
            Paths.get(MOCK_RESOURCE_PATH, ImplicitFormTransformer.EQUATIONS_FILE)
        );
  }

}