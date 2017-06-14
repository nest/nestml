/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.*;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static com.google.common.collect.Lists.newArrayList;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.AstCreator.createDeclaration;
import static org.nest.nestml._symboltable.symbols.VariableSymbol.resolve;
import static org.nest.utils.AstUtils.getVectorizedVariable;

/**
 * Takes SymPy result with the linear solution of the ODE and the source AST.
 * Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class LinearSolutionTransformer extends TransformerBase {
  public final static String P30_FILE = "P30.tmp";
  public final static String STATE_VECTOR_TMP_DECLARATIONS_FILE = "state.vector.tmp.declarations.tmp";
  public final static String STATE_VECTOR_UPDATE_STEPS_FILE = "state.vector.update.steps.tmp";
  public final static String STATE_VECTOR_TMP_BACK_ASSIGNMENTS_FILE = "state.vector.tmp.back.assignments.tmp";
  public final static String STATE_VARIABLES_FILE = "state.variables.tmp";
  public final static String PROPAGATOR_MATRIX_FILE = "propagator.matrix.tmp";
  public final static String PROPAGATOR_STEP_FILE = "propagator.step.tmp";

  private final Function<String, String> variableNameExtracter = initialValue -> initialValue.substring(0, initialValue.indexOf("PSCInitialValue"));
  private final Function<String, String> shapeNameExtracter = initialValue -> {
    final String variableName = initialValue.substring(0, initialValue.indexOf("PSCInitialValue"));
    return variableName.substring(variableName.indexOf("_") + 1, variableName.length());
  };


  public ASTNeuron addExactSolution(
      final ASTNeuron astNeuron,
      final Path P30File,
      final Path PSCInitialValueFile,
      final Path stateVariablesFile,
      final Path propagatorMatrixFile,
      final Path propagatorStepFile,
      final Path stateVectorTmpDeclarationsFile,
      final Path stateVectorUpdateStepsFile,
      final Path stateVectorTmpBackAssignmentsFile) {
    ASTNeuron workingVersion = astNeuron;
    workingVersion.getBody().addToInternalBlock(createDeclaration("__h__ ms = resolution()"));
    workingVersion = addAliasToInternals(astNeuron, P30File);
    workingVersion = addDeclarationsToInternals(workingVersion, PSCInitialValueFile);
    workingVersion = addDeclarationsToInternals(workingVersion, propagatorMatrixFile);

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

      addUpdatesWithPSCInitialValue(
          pathPSCInitialValueFile,
          body,
          variableNameExtracter,
          shapeNameExtracter);

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

        astNeuron.getBody().addToStateBlock(createDeclaration(stateVarDeclaration));
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
          .map(AstCreator::createAssignment)
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
        .map(AstCreator::createAssignment)
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
        final ASTDeclaration aliasAst = createDeclaration(tmpInternalVariables.get(j) + " real " + printVectorParameter(vectorizedVariable) + " = " + printer.print(nodesToReplace.get(j)));
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
        .map(AstCreator::createDeclaration)
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
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();
    astStmt.setSmall_Stmt(astSmall_stmt);

    astSmall_stmt.setDeclaration(astDeclaration);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }



}
