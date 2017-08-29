/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.codehaus.groovy.ast.Variable;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.ArrayList;
import java.util.List;

import static com.google.common.base.Preconditions.checkArgument;
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

    checkArgument(astNeuron.enclosingScopeIsPresent(),"Run symbol table creator.");

    ASTNeuron workingVersion = astNeuron;
    //addVariableToInternals(astNeuron, p30File);
    workingVersion.getBody().addToInternalBlock(createDeclaration("__h ms = resolution()"));
    workingVersion = addVariableToInternals(workingVersion, solverOutput.const_input);
    workingVersion = addVariableToInternals(workingVersion, solverOutput.ode_var_factor);

    final List<ASTFunctionCall> convolveCalls = AstUtils.getAll(astNeuron.getBody().getOdeBlock().get(), ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.CONVOLVE))
        .collect(toList());

    //collect convolve(currBuffer) invocations (formerly curr_sum() calls)
    final List<ASTFunctionCall> invocationsOnCurrBuffer = new ArrayList();
    for(ASTFunctionCall singleInvocation : convolveCalls){
      final Scope callScope = singleInvocation.getEnclosingScope().get();
      final String bufferName = singleInvocation.getArgs().get(1).getVariable().get().toString();
      if(VariableSymbol.resolve(bufferName,callScope).isCurrentBuffer()){
        invocationsOnCurrBuffer.add(singleInvocation);
      }
    }

    // Apply spikes from the buffer to the state variable
    for (ASTFunctionCall i_sum_call : invocationsOnCurrBuffer) {
      final String bufferName = AstUtils.toString(i_sum_call.getArgs().get(1));
      solverOutput.ode_var_update_instructions.add(astNeuron.getBody().getEquations().get(0).getLhs().getName() + "+=" + bufferName);
    }

    workingVersion = replaceIntegrateCallThroughPropagation(workingVersion, solverOutput.ode_var_update_instructions);
    return workingVersion;
  }

}
