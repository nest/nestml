/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTStmt;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.NESTMLASTCreator.createAlias;
import static org.nest.utils.AstUtils.getFunctionCall;

/**
 * Takes SymPy result with the exact solution of the Delta-shaped PSC and integrates it into the neuron instead of
 * the 'integrate'-call.
 * Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
class DeltaSolutionTransformer extends TransformerBase {
  final static String PROPAGATOR_STEP = "propagator.step.tmp";
  final static String ODE_TYPE = "solverType.tmp";
  final static String P30_FILE = "P30.tmp";

  ASTNeuron addExactSolution(
      final ASTNeuron astNeuron,
      final Path p30File,
      final Path propagatorStep) {

    // TODO can this variable be a vecotr?
    astNeuron.getBody().addToInternalBlock(createAlias("__h__ ms = resolution()"));
    addAliasToInternals(astNeuron, p30File);
    addP33ToInternals(astNeuron);
    addPropagatorStep(astNeuron, propagatorStep);

    return astNeuron;
  }

  /**
   * P33 can be computed from the delta shape definition as: exp(__h__/tau) where tau is the membrane time constant
   */
  private void addP33ToInternals(final ASTNeuron astNeuron) {
    // the function there, because otherwise this query wouldn't be made
    ASTFunctionCall deltaShape = getFunctionCall(
        PredefinedFunctions.DELTA,
        astNeuron.getBody().getODEBlock().get()).get();
    // delta is define as delta(t, tau) -> get the second argument
    // per context condition must be checked, that only 'simple' argument, e.g. qualified name, is provided
    final String tauConstant = deltaShape.getArgs().get(1).getVariable().get().toString();
    // TODO it could be a vector
    final String p33Declaration = "__P33__ real = exp(-__h__ / " + tauConstant + ")";
    final ASTAliasDecl astDeclaration =  NESTMLASTCreator.createAlias(p33Declaration);
    astNeuron.getBody().addToInternalBlock(astDeclaration);
  }

  private void addPropagatorStep(ASTNeuron astNeuron, Path propagatorStepFile) {
    try {
      final List<ASTStmt> propagatorSteps = Lists.newArrayList();


      final ASTAssignment updateAssignment = NESTMLASTCreator.createAssignment(Files.lines(propagatorStepFile).findFirst().get());
      final ASTAssignment applyP33 = NESTMLASTCreator.createAssignment(updateAssignment.getLhsVarialbe() + "*=" +  "__P33__" );

      propagatorSteps.add(statement(applyP33));
      propagatorSteps.add(statement(updateAssignment));

      final List<ASTFunctionCall> i_sumCalls = AstUtils.getAll(astNeuron.getBody().getODEBlock().get(), ASTFunctionCall.class)
          .stream()
          .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.CURR_SUM))
          .collect(toList());

      // Apply spikes from the buffer to the state variable
      for (ASTFunctionCall i_sum_call : i_sumCalls) {
        final String bufferName = AstUtils.toString(i_sum_call.getArgs().get(1));
        final ASTAssignment applySpikes = NESTMLASTCreator.createAssignment(updateAssignment.getLhsVarialbe() + "+=" + bufferName);
        propagatorSteps.add(statement(applySpikes));
      }

      replaceODEPropagationStep(astNeuron, propagatorSteps);
    } catch (IOException e) {
      throw new RuntimeException("Cannot parse propagator step for the delta function", e);
    }
  }

}
