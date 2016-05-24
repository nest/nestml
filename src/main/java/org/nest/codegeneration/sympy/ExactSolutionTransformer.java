/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.*;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;

/**
 * Takes SymPy result and the source AST. Produces an altered AST with the the exact solution.
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  private final SymPyOutput2NESTMLConverter converter2NESTML = new SymPyOutput2NESTMLConverter();

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
    ASTNeuron workingVersion = addP30(astNeuron, P00File);
    astNeuron.getBody().addToInternalBlock(converter2NESTML.convertStringToAlias("h ms = resolution()"));
    workingVersion = addDeclarationsInternalBlock(workingVersion, PSCInitialValueFile);
    workingVersion = addDeclarationsInternalBlock(workingVersion, propagatorMatrixFile);
    workingVersion = addStateVariables(stateVariablesFile, workingVersion);
    workingVersion = addStateVariableUpdatesToDynamics(
        workingVersion,
        PSCInitialValueFile,
        stateVectorTmpDeclarationsFile,
        stateVectorUpdateStepsFile,
        stateVectorTmpBackAssignmentsFile);

    workingVersion = replaceODEPropagationStep(workingVersion, propagatorStepFile);

    return workingVersion;
  }


  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addP30(
      final ASTNeuron astNeuron,
      final Path pathToP00File) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertToAliases(pathToP00File).get(0);

    astNeuron.getBody().addToInternalBlock(p00Declaration);
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addDeclarationsInternalBlock(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile) {
    final Scope scope = ((ScopeSpanningSymbol)astNeuron.getSymbol().get()).getSpannedScope(); // valid, after the symboltable is created

    final List<ASTAliasDecl> pscInitialValues = converter2NESTML.convertToAliases(pathPSCInitialValueFile);
    for (final ASTAliasDecl astAliasDecl:pscInitialValues) {
      // filter step: filter all variables, which very added during model analysis, but not added to the symbol table
      final List<ASTVariable> variables = ASTNodes
          .getAll(astAliasDecl.getDeclaration(), ASTVariable.class).stream()
          .filter(astVariable -> VariableSymbol.resolveIfExists(astVariable.toString(), scope).isPresent())
          .collect(Collectors.toList());

      checkState(astNeuron.enclosingScopeIsPresent());
      
      Optional<VariableSymbol> vectorizedVariable = variables.stream()
          .map(astVariable -> resolve(astVariable.toString(), scope))
          .filter(variableSymbol -> variableSymbol.getVectorParameter().isPresent())
          .findAny();
      if (vectorizedVariable.isPresent()) {
        // the existence of the array parameter is ensured by the query
        astAliasDecl.getDeclaration().setSizeParameter(vectorizedVariable.get().getVectorParameter().get());
      }

    }

    pscInitialValues.stream().forEach(initialValue -> astNeuron.getBody().addToInternalBlock(initialValue));

    return astNeuron;
  }

  ASTNeuron addStateVariableUpdatesToDynamics(
      final ASTNeuron astNeuron,
      final Path pathPSCInitialValueFile,
      final Path stateVectorTmpDeclarationsFile,
      final Path stateVectorUpdateStepsFile,
      final Path stateVectorTmpBackAssignmentsFile) {
    try {
      checkState(astNeuron.getBody().getEquations().isPresent(),  "The model has no ODES.");
      final ASTBody body = astNeuron.getBody();

      addStateUpdates(
          stateVectorTmpDeclarationsFile,
          stateVectorUpdateStepsFile,
          stateVectorTmpBackAssignmentsFile,
          body);
      addPSCInitialValuesUpdates(pathPSCInitialValueFile, body);

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
      final List<String> stateVariables = Files.lines(stateVariablesFile)
          .map(stateVariable -> stateVariable)
          .collect(toList());
      final List<VariableSymbol> correspondingShapeSymbols = stateVariables
          .stream()
          .map(this::getShapeNameFromStateVariable)
          .map(shapeName -> resolve(shapeName, scope))
          .collect(Collectors.toList());
      for (int i = 0; i < stateVariables.size(); ++i) {
        final String vectorDatatype = correspondingShapeSymbols.get(i).isVector()?"[" + correspondingShapeSymbols.get(i).getVectorParameter().get() + "]":"";
        final String stateVarDeclaration = stateVariables.get(i)+ " real " + vectorDatatype;

        astNeuron.getBody().addToStateBlock(converter2NESTML.convertStringToAlias(stateVarDeclaration));
      }

      return astNeuron;
    } catch (IOException e) {
      throw new RuntimeException("Cannot parse the file with state variables.", e);
    }

  }

  private void addStateUpdates(
      final Path stateVectorTmpDeclarationsFile,
      final Path stateVectorUpdateStepsFile,
      final Path stateVectorTmpBackAssignmentsFile, final ASTBody astBody) throws IOException {
    checkState(astBody.getEnclosingScope().isPresent(), "Run symbol table creator");

    final List<ASTDeclaration> tmpDeclarations = Files.lines(stateVectorTmpDeclarationsFile)
        .map(converter2NESTML::convertStringToDeclaration)
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


    final List<String> stateUpdates = Files
        .lines(stateVectorUpdateStepsFile)
        .collect(toList());
    final List<ASTAssignment> stateUpdateAssignments = stateUpdates
        .stream()
        .map(converter2NESTML::convertStringToAssignment)
        .collect(toList());


    final List<ASTAssignment> backAssignments = Files.lines(stateVectorTmpBackAssignmentsFile)
        .map(converter2NESTML::convertStringToAssignment)
        .collect(Collectors.toList());

    tmpDeclarations.forEach(tmpDeclaration -> addDeclarationToDynamics(astBody, tmpDeclaration));
    stateUpdateAssignments.forEach(varAssignment -> addAssignmentToDynamics(astBody, varAssignment));
    backAssignments.forEach(varAssignment -> addAssignmentToDynamics(astBody, varAssignment));
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

  private void addPSCInitialValuesUpdates(final Path pathPSCInitialValueFile, final ASTBody body) {
    final List<ASTFunctionCall> i_sumCalls = ASTNodes.getAll(body.getEquations().get(), ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM))
        .collect(toList());

    final List<ASTAliasDecl> pscInitialValues = converter2NESTML.convertToAliases(pathPSCInitialValueFile);
    for (final ASTAliasDecl pscInitialValue:pscInitialValues) {
      final String pscInitialValueAsString = pscInitialValue.getDeclaration().getVars().get(0);
      final String variableName = pscInitialValueAsString.substring(0, pscInitialValueAsString.indexOf("PSCInitialValue"));
      final String shapeName = variableName.substring(variableName.indexOf("_") + 1, variableName.length());
      for (ASTFunctionCall i_sum_call:i_sumCalls) {
        final String shapeNameInCall = ASTNodes.toString(i_sum_call.getArgs().get(0));
        if (shapeNameInCall.equals(shapeName)) {
          final String bufferName = ASTNodes.toString(i_sum_call.getArgs().get(1));
          final ASTAssignment pscUpdateStep = converter2NESTML
              .convertStringToAssignment(variableName + " += " +  pscInitialValueAsString + " * "+ bufferName + ".getSum(t)");
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

  ASTNeuron replaceODEPropagationStep(final ASTNeuron astNeuron, final Path updateStepFile) {

    final ASTBody astBodyDecorator = astNeuron.getBody();
    final IntegrateFunctionCollector odeCollector = new IntegrateFunctionCollector();

    try {
      final List<ASTSmall_Stmt> propagatorSteps = Files.lines(updateStepFile)
          .map(converter2NESTML::convertStringToAssignment)
          .map(this::convertToSmallStatement)
          .collect(toList());
      odeCollector.startVisitor(astBodyDecorator.getDynamics().get(0));

      if (odeCollector.getFoundOde().isPresent()) {
        final Optional<ASTNode> smallStatement = ASTNodes.getParent(odeCollector.getFoundOde().get(), astNeuron);
        checkState(smallStatement.isPresent());
        checkState(smallStatement.get() instanceof ASTSmall_Stmt);
        final ASTSmall_Stmt integrateCall = (ASTSmall_Stmt) smallStatement.get();

        final Optional<ASTNode> simpleStatement = ASTNodes.getParent(smallStatement.get(), astNeuron);
        checkState(simpleStatement.isPresent());
        checkState(simpleStatement.get() instanceof ASTSimple_Stmt);
        final ASTSimple_Stmt astSimpleStatement = (ASTSimple_Stmt) simpleStatement.get();
        int integrateFunction = astSimpleStatement.getSmall_Stmts().indexOf(integrateCall);
        astSimpleStatement.getSmall_Stmts().remove(integrateCall);
        astSimpleStatement.getSmall_Stmts().addAll(integrateFunction, propagatorSteps);

        return astNeuron;
      } else {
        Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
        return astNeuron;
      }
    } catch (IOException e) {
      final String msg = "Cannot parse assignment statement.";
      throw new RuntimeException(msg, e);
    }

  }

  private ASTSmall_Stmt convertToSmallStatement(final ASTAssignment astAssignment) {
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();
    astSmall_stmt.setAssignment(astAssignment);
    return astSmall_stmt;
  }

  private class IntegrateFunctionCollector implements NESTMLInheritanceVisitor {
    // Initialized by null and set to the actual value
    private ASTFunctionCall foundOde = null;

    void startVisitor(ASTNESTMLNode node) {
      node.accept(this);
    }

    @Override
    public void visit(final ASTFunctionCall astFunctionCall) {
      // TODO actually works only for the first ode
      if (astFunctionCall.getCalleeName().equals("integrate")) {
        foundOde = astFunctionCall;
      }
    }

    Optional<ASTFunctionCall> getFoundOde() {
      return Optional.ofNullable(foundOde);
    }

  }

}
