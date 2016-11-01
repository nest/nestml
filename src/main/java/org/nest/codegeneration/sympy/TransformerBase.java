package org.nest.codegeneration.sympy;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.*;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.function.Function;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.NESTMLASTCreator.createAliases;
import static org.nest.codegeneration.sympy.NESTMLASTCreator.createAssignment;
import static org.nest.utils.AstUtils.getVectorizedVariable;

/**
 * Provides common methods for solver transformations.
 *
 * @author plotnikov
 */
public class TransformerBase {
  public final static String SOLVER_TYPE = "solverType.tmp";
  public final static String PSC_INITIAL_VALUE_FILE = "pscInitialValues.tmp";
  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addAliasToInternals(
      final ASTNeuron astNeuron,
      final Path declarationFile) {

    final ASTAliasDecl p00Declaration = createAliases(declarationFile).get(0);

    astNeuron.getBody().addToInternalBlock(p00Declaration);
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addDeclarationsToInternals(
      final ASTNeuron astNeuron,
      final Path declarationsFile) {
    checkState(astNeuron.getSymbol().isPresent());
    final Scope scope = ((ScopeSpanningSymbol)astNeuron.getSymbol().get()).getSpannedScope(); // valid, after the symboltable is created

    final List<ASTAliasDecl> pscInitialValues = createAliases(declarationsFile);
    for (final ASTAliasDecl astAliasDecl:pscInitialValues) {
      // filter step: filter all variables, which very added during model analysis, but not added to the symbol table
      final Optional<VariableSymbol> vectorizedVariable = getVectorizedVariable(astAliasDecl.getDeclaration(), scope);
      if (vectorizedVariable.isPresent()) {
        // the existence of the array parameter is ensured by the query
        astAliasDecl.getDeclaration().setSizeParameter(vectorizedVariable.get().getVectorParameter().get());
      }

    }

    pscInitialValues.forEach(initialValue -> astNeuron.getBody().addToInternalBlock(initialValue));

    return astNeuron;
  }

  ASTNeuron replaceODEPropagationStep(final ASTNeuron astNeuron, final Path updateStepFile) {
    try {
    final List<ASTStmt> propagatorSteps = Files.lines(updateStepFile)
        .map(NESTMLASTCreator::createAssignment)
        .map(this::statement)
        .collect(toList());
      return replaceODEPropagationStep(astNeuron, propagatorSteps);

    } catch (IOException e) {
      throw new RuntimeException("Cannot parse assignment statement.", e);
    }
  }

  ASTNeuron replaceODEPropagationStep(final ASTNeuron astNeuron, List<ASTStmt> propagatorSteps) {

    final ASTBody astBodyDecorator = astNeuron.getBody();

    // It must work for multiple integrate calls!
    final Optional<ASTFunctionCall> integrateCall = AstUtils.getFunctionCall(
        PredefinedFunctions.INTEGRATE_ODES,
        astBodyDecorator.getDynamics().get(0));

    if (integrateCall.isPresent()) {
      final Optional<ASTNode> smallStatement = AstUtils.getParent(integrateCall.get(), astNeuron);
      checkState(smallStatement.isPresent());
      checkState(smallStatement.get() instanceof ASTSmall_Stmt);

      final Optional<ASTNode> statement = AstUtils.getParent(smallStatement.get(), astNeuron);
      checkState(statement.isPresent());
      checkState(statement.get() instanceof ASTStmt);

      final Optional<ASTNode> block = AstUtils.getParent(statement.get(), astNeuron);
      checkState(block.isPresent());
      checkState(block.get() instanceof ASTBlock);

      final ASTBlock astBlock = (ASTBlock) block.get();
      for (int i = 0; i < astBlock.getStmts().size(); ++i) {
        if (astBlock.getStmts().get(i).equals(statement.get())) {
          astBlock.getStmts().remove(i);
          astBlock.getStmts().addAll(i, propagatorSteps);
          break;
        }
      }

      return astNeuron;
    } else {
      Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
      return astNeuron;
    }


  }

  /**
   * Add updates of state variables with the PSC initial value and corresponding inputs from buffers.
   *
   * @param pathPSCInitialValueFile File with a list of PSC initial values for the corresponding shapes
   * @param body The astnode of the neuron to which update assignments must be added
   * @param nameHandler In some cases the name of the state variable extracted from the assignment must be transformed
   *                    (G'_PSCInitialValue would be an invalid name, therefore, G__D_PSCInitialValue is used, where
   *                    G' is the name of the state variable)
   */
  void addUpdatesWithPSCInitialValue(
      final Path pathPSCInitialValueFile,
      final ASTBody body,
      final Function<String, String> stateVariableNameExtracter,
      final Function<String, String> shapeNameExtracter) {
    final List<ASTFunctionCall> i_sumCalls = ODETransformer.get_sumFunctionCalls(body.getODEBlock().get());

    final List<ASTAliasDecl> pscInitialValues = createAliases(pathPSCInitialValueFile);
    for (final ASTAliasDecl pscInitialValue:pscInitialValues) {
      final String pscInitialValueAsString = pscInitialValue.getDeclaration().getVars().get(0);


      final String shapeName = shapeNameExtracter.apply(pscInitialValueAsString);
      final String variableName = stateVariableNameExtracter.apply(pscInitialValueAsString);
      for (ASTFunctionCall i_sum_call:i_sumCalls) {
        final String shapeNameInCall = AstUtils.toString(i_sum_call.getArgs().get(0));
        if (shapeNameInCall.equals(shapeName)) {
          final String bufferName = AstUtils.toString(i_sum_call.getArgs().get(1));
          final ASTAssignment pscUpdateStep = createAssignment(
              variableName + " += " +  pscInitialValueAsString + " * "+ bufferName + ".get_sum(t)");
          addAssignmentToDynamics(body, pscUpdateStep);
        }

      }

    }

  }

  void addAssignmentToDynamics(
      final ASTBody astBodyDecorator,
      final ASTAssignment yVarAssignment) {
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();

    astStmt.setSmall_Stmt(astSmall_stmt);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(yVarAssignment);

    astBodyDecorator.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }

  ASTStmt statement(final ASTAssignment astAssignment) {
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();
    final ASTStmt astStmt = SPLNodeFactory.createASTStmt();
    astSmall_stmt.setAssignment(astAssignment);
    astStmt.setSmall_Stmt(astSmall_stmt);
    return astStmt;
  }

}
