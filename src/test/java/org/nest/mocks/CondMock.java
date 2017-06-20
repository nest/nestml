/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.mocks;

import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.sympy.ImplicitFormTransformer;
import org.nest.codegeneration.sympy.EquationBlockProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Provides a mock for the cond_alpha neuron defined with an ode.
 *
 * @author plotnikov
 */
public class CondMock extends EquationBlockProcessor {
  private final static String MOCK_RESOURCE_PATH = "src/test/resources/codegeneration/sympy/cond/";


}