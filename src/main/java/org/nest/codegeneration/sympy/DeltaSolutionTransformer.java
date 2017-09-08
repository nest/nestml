/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.utils.AstUtils;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.AstCreator.createDeclaration;

/**
 * Takes SymPy result with the exact solution of the Delta-shaped PSC and integrates it into the neuron instead of
 * the 'integrate'-call.
 * Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
class DeltaSolutionTransformer extends TransformerBase {

  ASTNeuron addExactSolution(
      final SolverOutput solverOutput, final ASTNeuron astNeuron) {

    ASTNeuron workingVersion = astNeuron;
    //addVariableToInternals(astNeuron, p30File);
    workingVersion.addToInternalBlock(createDeclaration("__h ms = resolution()"));
    workingVersion = addVariableToInternals(workingVersion, solverOutput.const_input);
    workingVersion = addVariableToInternals(workingVersion, solverOutput.ode_var_factor);

    final List<ASTFunctionCall> i_sumCalls = AstUtils.getAll(astNeuron.findEquationsBlock().get(), ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.CURR_SUM))
        .collect(toList());

    // Apply spikes from the buffer to the state variable
    for (ASTFunctionCall i_sum_call : i_sumCalls) {
      final String bufferName = AstUtils.toString(i_sum_call.getArgs().get(1));
      solverOutput.ode_var_update_instructions.add(astNeuron.getEquations().get(0).getLhs().getName() + "+=" + bufferName);
    }

    workingVersion = replaceIntegrateCallThroughPropagation(workingVersion, solverOutput.ode_var_update_instructions);
    return workingVersion;
  }

}
