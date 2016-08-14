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
import org.nest.utils.ASTUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.NESTMLASTCreator.createAlias;
import static org.nest.utils.ASTUtils.getFunctionCall;

/**
 * Takes SymPy result with the linear solution of the ODE and the source AST.
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
  private void addP33ToInternals(ASTNeuron astNeuron) {
    // the function there, because otherwise this query wouldn't be made
    ASTFunctionCall deltaShape = getFunctionCall(
        PredefinedFunctions.DELTA,
        astNeuron.getBody().getODEBlock().get()).get();
    // delta is define as delta(t, tau) -> get the second argument
    // per context condition must be checked, that only 'simple' argument, e.g. qualified name, is provided
    final String tauConstant = deltaShape.getArgs().get(1).getVariable().get().toString();
    // TODO it could be a vector
    final String p33Declaration = "P33 real = exp(__h__ / " + tauConstant + ")";
    final ASTAliasDecl astDeclaration =  NESTMLASTCreator.createAlias(p33Declaration);
    astNeuron.getBody().addToInternalBlock(astDeclaration);
  }

  private void addPropagatorStep(ASTNeuron astNeuron, Path propagatorStepFile) {
    try {
      final List<ASTStmt> propagatorSteps = Lists.newArrayList();

      final ASTAssignment updateAssignemt = NESTMLASTCreator.createAssignment(Files.lines(propagatorStepFile).findFirst().get());
      propagatorSteps.add(statement(updateAssignemt));


      final List<ASTFunctionCall> i_sumCalls = ASTUtils.getAll(astNeuron.getBody().getODEBlock().get(), ASTFunctionCall.class)
          .stream()
          .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM))
          .collect(toList());

      for (ASTFunctionCall i_sum_call : i_sumCalls) {
        final String bufferName = ASTUtils.toString(i_sum_call.getArgs().get(1));
        final ASTAssignment applySpikes = NESTMLASTCreator.createAssignment(updateAssignemt.getLhsVarialbe() + "+=" + bufferName + ".getSum(t)");
        propagatorSteps.add(statement(applySpikes));
      }

      replaceODEPropagationStep(astNeuron, propagatorSteps);
    } catch (IOException e) {
      throw new RuntimeException("Cannot parse propagator step for the delta function", e);
    }
  }

}
