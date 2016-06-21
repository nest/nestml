/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.*;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static com.google.common.collect.Lists.newArrayList;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.NESTMLASTCreator.*;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;
import static org.nest.utils.ASTUtils.getVectorizedVariable;

/**
 * Takes SymPy result with the linear solution of the ODE and the source AST.
 * Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class LinearSolutionTransformer extends TransformerBase {

  public final static String P30_FILE = "P30.tmp";
  public final static String PSC_INITIAL_VALUE_FILE = "pscInitialValues.tmp";
  public final static String STATE_VECTOR_TMP_DECLARATIONS_FILE = "state.vector.tmp.declarations.tmp";
  public final static String STATE_VECTOR_UPDATE_STEPS_FILE = "state.vector.update.steps.tmp";
  public final static String STATE_VECTOR_TMP_BACK_ASSIGNMENTS_FILE = "state.vector.tmp.back.assignments.tmp";
  public final static String STATE_VARIABLES_FILE = "state.variables.tmp";
  public final static String PROPAGATOR_MATRIX_FILE = "propagator.matrix.tmp";
  public final static String PROPAGATOR_STEP_FILE = "propagator.step.tmp";
  final static String ODE_TYPE = "solverType.tmp";

  public ASTNeuron addExactSolution(
      final ASTNeuron astNeuron,
      final Path P00File,
      final Path PSCInitialValueFile,
      final Path stateVariablesFile,
      final Path propagatorMatrixFile,
      final Path propagatorStepFile,
      final Path stateVectorTmpDeclarationsFile,
      final Path stateVectorUpdateStepsFile,
      final Path stateVectorTmpBackAssignmentsFile) {
    ASTNeuron workingVersion = addAliasToInternals(astNeuron, P00File);
    workingVersion.getBody().addToInternalBlock(createAlias("__h__ ms = resolution()"));

    workingVersion = addDeclarationsInternalBlock(workingVersion, PSCInitialValueFile);
    workingVersion = addDeclarationsInternalBlock(workingVersion, propagatorMatrixFile);

    workingVersion = addStateVariableUpdatesToDynamics(
        workingVersion,
        PSCInitialValueFile,
        stateVectorTmpDeclarationsFile,
        stateVariablesFile,
        stateVectorUpdateStepsFile,
        stateVectorTmpBackAssignmentsFile);
    // oder is important, otherwise addStateVariableUpdatesToDynamics will try to resolve state variables,
    // for which nor symbol are added. TODO filter them
    workingVersion = addStateVariables(stateVariablesFile, workingVersion);
    workingVersion = replaceODEPropagationStep(workingVersion, propagatorStepFile);

    return workingVersion;
  }


  private ASTNeuron addStateVariableUpdatesToDynamics(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile,
      final Path stateVectorTmpDeclarationsFile,
      final Path stateVectorVariablesFile,
      final Path stateVectorUpdateStepsFile,
      final Path stateVectorTmpBackAssignmentsFile) {
    try {
      checkState(astNeuron.getBody().getODEBlock().isPresent(),  "The model has no ODES.");
      final ASTBody body = astNeuron.getBody();

      addStateUpdates(
          stateVectorTmpDeclarationsFile,
          stateVectorVariablesFile,
          stateVectorUpdateStepsFile,
          stateVectorTmpBackAssignmentsFile,
          body);

      addUpdatesWithPSCInitialValue(pathPSCInitialValueFile, body);

      return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot solveODE stateVector output from the SymPy solver", e);
    }
  }

  ASTNeuron addStateVariables(final Path stateVariablesFile, final ASTNeuron astNeuron) {
    checkState(astNeuron.getBody().getEnclosingScope().isPresent());
    final Scope scope = astNeuron.getBody().getEnclosingScope().get();

    try {
      final List<String> stateVariables = Files.lines(stateVariablesFile).collect(toList());
      final List<VariableSymbol> correspondingShapeSymbols = stateVariables
          .stream()
          .map(this::getShapeNameFromStateVariable)
          .map(shapeName -> resolve(shapeName, scope))
          .collect(Collectors.toList());
      for (int i = 0; i < stateVariables.size(); ++i) {
        final String vectorDatatype = correspondingShapeSymbols.get(i).isVector()?"[" + correspondingShapeSymbols.get(i).getVectorParameter().get() + "]":"";
        final String stateVarDeclaration = stateVariables.get(i)+ " real " + vectorDatatype;

        astNeuron.getBody().addToStateBlock(createAlias(stateVarDeclaration));
      }

      return astNeuron;
    } catch (IOException e) {
      throw new RuntimeException("Cannot parse the file with state variables.", e);
    }

  }

  private void addStateUpdates(
      final Path stateVectorTmpDeclarationsFile,
      final Path stateVectorVariablesFile,
      final Path stateVectorUpdateStepsFile,
      final Path stateVectorTmpBackAssignmentsFile,
      final ASTBody astBody) throws IOException {
    checkState(astBody.getEnclosingScope().isPresent(), "Run symbol table creator");

    final List<ASTDeclaration> tmpDeclarations = computeTmpVariableDeclarations(stateVectorTmpDeclarationsFile, astBody);
    final List<ASTAssignment> stateUpdateAssignments = computeUpdateStateAssignments(
        stateVectorVariablesFile,
        stateVectorUpdateStepsFile,
        astBody);
    final List<ASTAssignment> backAssignments = computeBackAssignments(stateVectorTmpBackAssignmentsFile);

    tmpDeclarations.forEach(tmpDeclaration -> addDeclarationToDynamics(astBody, tmpDeclaration));
    stateUpdateAssignments.forEach(varAssignment -> addAssignmentToDynamics(astBody, varAssignment));
    backAssignments.forEach(varAssignment -> addAssignmentToDynamics(astBody, varAssignment));
  }

  private List<ASTAssignment> computeBackAssignments(Path stateVectorTmpBackAssignmentsFile) throws IOException {
    return Files.lines(stateVectorTmpBackAssignmentsFile)
          .map(NESTMLASTCreator::createAssignment)
          .collect(Collectors.toList());
  }

  private List<ASTAssignment> computeUpdateStateAssignments(
      final Path stateVectorVariablesFile,
      final Path stateVectorUpdateStepsFile,
      final ASTBody astBody) throws IOException {
    final ExpressionsPrettyPrinter printer = new ExpressionsPrettyPrinter();
    final Scope scope = astBody.getEnclosingScope().get();
    final List<String> stateUpdates = Files.lines(stateVectorUpdateStepsFile).collect(toList());
    final List<ASTAssignment> stateUpdatesASTs = stateUpdates
        .stream()
        .map(NESTMLASTCreator::createAssignment)
        .collect(toList());

    final List<ASTExpr> rhsExpressions = stateUpdatesASTs
        .stream()
        .map(ASTAssignment::getExpr)
        .collect(toList());

    final List<String> stateVariableNames = newArrayList();
    stateVariableNames.addAll(astBody.getStateSymbols()
        .stream()
        .map(VariableSymbol::getName)
        .collect(toList()));

    stateVariableNames.addAll(Files.lines(stateVectorVariablesFile).collect(toList()));

    for (int i = 0; i < rhsExpressions.size(); ++i) {
      final ASTExpr expr = rhsExpressions.get(i);
      final ExpressionFolder expressionFolder = new ExpressionFolder();
      // now, variables in the expression are replaced, but they would be undefined in the model
      // ant they are changed in the expressions stored in stateUpdatesASTs
      expressionFolder.fold(expr, stateVariableNames, "__P" + i);
      // add these additional variables to the internal block
      final List<ASTExpr> nodesToReplace = expressionFolder.getNodesToReplace();
      final List<String> tmpInternalVariables = expressionFolder.getInternalVariables();
      for (int j = 0; j < nodesToReplace.size(); ++j) {
        final Optional<VariableSymbol> vectorizedVariable = getVectorizedVariable(nodesToReplace.get(j), scope);
        final ASTAliasDecl aliasAst = createAlias(tmpInternalVariables.get(j) + " real " + printVectorParameter(vectorizedVariable) + " = " + printer.print(nodesToReplace.get(j)));
        astBody.addToInternalBlock(aliasAst);
      }

    }
    return stateUpdatesASTs;
  }

  private String printVectorParameter(Optional<VariableSymbol> vectorizedVariable) {
    return vectorizedVariable.isPresent()?"[" + vectorizedVariable.get().getVectorParameter().get() + "]":"";
  }

  private List<ASTDeclaration> computeTmpVariableDeclarations(Path stateVectorTmpDeclarationsFile, ASTBody astBody) throws IOException {
    final List<ASTDeclaration> tmpDeclarations = Files.lines(stateVectorTmpDeclarationsFile)
        .map(NESTMLASTCreator::createDeclaration)
        .collect(Collectors.toList());

    final List<VariableSymbol> shapeForVariable = tmpDeclarations
        .stream()
        .map(astDeclaration -> astDeclaration.getVars().get(0))
        .map(this::getShapeNameFromStateVariable)
        .map(shapeName -> resolve(shapeName, astBody.getEnclosingScope().get()))
        .collect(Collectors.toList());

    for (int varIndex = 0; varIndex < tmpDeclarations.size(); ++varIndex) {
      if (shapeForVariable.get(varIndex).isVector()) {
        tmpDeclarations.get(varIndex).setSizeParameter(shapeForVariable.get(varIndex).getVectorParameter().get());
      }
    }
    return tmpDeclarations;
  }

  /**
   * Dependent on the ODE order the state variable name can have a postfix '_tmp'. The shape name is either
   * y2_I_shape_in_tmp or y2_I_shape_in
   * @param stateVariableName Statevariable name generated by the solver script
   * @return Shapename as string
   */
  private String getShapeNameFromStateVariable(final String stateVariableName) {
    if (stateVariableName.endsWith("_tmp")) {
      return stateVariableName.substring(stateVariableName.indexOf("_") + 1, stateVariableName.indexOf("_tmp"));
    }
    else {
      return stateVariableName.substring(stateVariableName.indexOf("_") + 1);
    }
  }

  private void addDeclarationToDynamics(
      final ASTBody astBodyDecorator,
      final ASTDeclaration astDeclaration) {
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    final ASTSimple_Stmt astSimpleStmt = SPLNodeFactory.createASTSimple_Stmt();
    final List<ASTSmall_Stmt> astSmallStmts = Lists.newArrayList();
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();

    astStmt.setSimple_Stmt(astSimpleStmt);
    astSmallStmts.add(astSmall_stmt);
    astSimpleStmt.setSmall_Stmts(astSmallStmts);

    astSmall_stmt.setDeclaration(astDeclaration);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }

  private void addUpdatesWithPSCInitialValue(final Path pathPSCInitialValueFile, final ASTBody body) {
    final List<ASTFunctionCall> i_sumCalls = ASTUtils.getAll(body.getODEBlock().get(), ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM))
        .collect(toList());

    final List<ASTAliasDecl> pscInitialValues = createAliases(pathPSCInitialValueFile);
    for (final ASTAliasDecl pscInitialValue:pscInitialValues) {
      final String pscInitialValueAsString = pscInitialValue.getDeclaration().getVars().get(0);
      final String variableName = pscInitialValueAsString.substring(0, pscInitialValueAsString.indexOf("PSCInitialValue"));
      final String shapeName = variableName.substring(variableName.indexOf("_") + 1, variableName.length());
      for (ASTFunctionCall i_sum_call:i_sumCalls) {
        final String shapeNameInCall = ASTUtils.toString(i_sum_call.getArgs().get(0));
        if (shapeNameInCall.equals(shapeName)) {
          final String bufferName = ASTUtils.toString(i_sum_call.getArgs().get(1));
          final ASTAssignment pscUpdateStep = createAssignment(variableName + " += " +  pscInitialValueAsString + " * "+ bufferName + ".getSum(t)");
          addAssignmentToDynamics(body, pscUpdateStep);
        }

      }

    }

  }

  private void addAssignmentToDynamics(
      final ASTBody astBodyDecorator,
      final ASTAssignment yVarAssignment) {
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    final ASTSimple_Stmt astSimpleStmt = SPLNodeFactory.createASTSimple_Stmt();
    final List<ASTSmall_Stmt> astSmallStmts = Lists.newArrayList();
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();

    astStmt.setSimple_Stmt(astSimpleStmt);
    astSmallStmts.add(astSmall_stmt);
    astSimpleStmt.setSmall_Stmts(astSmallStmts);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(yVarAssignment);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }



}
