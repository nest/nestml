/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.mocks;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.sympy.LinearSolutionTransformer;
import org.nest.codegeneration.sympy.OdeProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Provides a mock for the psc_alpha neuron defined with an ode.
 *
 * @author plotnikov
 */
public class PSCMock extends OdeProcessor {
  private final static String MOCK_RESOURCE_PATH = "src/test/resources/codegeneration/sympy/psc/";

  @Override
  protected ASTNeuron handleNeuronWithODE(final ASTNeuron astNeuron, ASTNESTMLCompilationUnit artifactRoot, final Path outputBase) {
    Log.trace("Uses PSC mock", this.getClass().getName());
    return getLinearSolutionTransformer().addExactSolution(
            astNeuron,
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.P30_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.PSC_INITIAL_VALUE_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VARIABLES_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.PROPAGATOR_MATRIX_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.PROPAGATOR_STEP_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VECTOR_TMP_DECLARATIONS_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VECTOR_UPDATE_STEPS_FILE),
            Paths.get(MOCK_RESOURCE_PATH, astNeuron.getName() + "." + LinearSolutionTransformer.STATE_VECTOR_TMP_BACK_ASSIGNMENTS_FILE)
        );
  }

}