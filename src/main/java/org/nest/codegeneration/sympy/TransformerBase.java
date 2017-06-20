package org.nest.codegeneration.sympy;

import de.monticore.ast.ASTNode;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.nestml._ast.*;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.AstCreator.createAssignment;
import static org.nest.codegeneration.sympy.AstCreator.createDeclarations;

/**
 * Provides common methods for AST transformations which are performed after SymPy analysis.
 *
 * @author plotnikov
 */
public class TransformerBase {
  final NESTMLParser parser = new NESTMLParser();
  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addVariableToInternals(
      final ASTNeuron astNeuron,
      final Path declarationFile) {

    final ASTDeclaration astDeclaration = createDeclarations(declarationFile).get(0);

    astNeuron.getBody().addToInternalBlock(astDeclaration);
    return astNeuron;
  }

  /**
   * Add a list with declarations to the internals block in the neuron.
   */
  ASTNeuron addVariablesToInternals(
      final ASTNeuron astNeuron,
      final List<Map.Entry<String, String>> declarationsFile) {
    declarationsFile.forEach(declaration -> addVariableToInternals(astNeuron, declaration));
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  ASTNeuron addVariableToInternals(
      final ASTNeuron astNeuron,
      final Map.Entry<String, String> declaration) {
    try {
      ASTExpr tmp = parser.parseExpr(new StringReader(declaration.getValue())).get(); // must not fail by constuction
      final Optional<VariableSymbol> vectorVariable = AstUtils.getVectorizedVariable(tmp, astNeuron.getSpannedScope().get());

      final String declarationString = declaration.getKey() + " real" +
                                       vectorVariable.map(variableSymbol -> "[" + variableSymbol.getVectorParameter().get() + "]").orElse("")
                                       + " = " + declaration.getValue();
      final ASTDeclaration astDeclaration = parser.parseDeclaration(new StringReader(declarationString)).get();
      vectorVariable.ifPresent(var -> astDeclaration.setSizeParameter(var.getVectorParameter().get()));
      astNeuron.getBody().addToInternalBlock(astDeclaration);
      return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Must not fail by construction.");
    }

  }

  ASTNeuron replaceIntegrateCallThroughPropagation(final ASTNeuron astNeuron, List<String> propagatorSteps) {

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
          astBlock.getStmts().addAll(i, propagatorSteps.stream().map(AstCreator::createStatement).collect(toList()));
          break;
        }
      }
      return astNeuron;
    } else {
      Log.trace(
          "The model has defined an ODE. But its solution is not used in the update state.",
          this.getClass().getSimpleName());
      return astNeuron;
    }

  }

  /**
   * Add updates of state variables with the PSC initial value and corresponding inputs from buffers.
   */
  void addUpdatesWithPSCInitialValue(
      final SolverOutput solverOutput,
      final ASTBody body,
      final Function<String, String> stateVariableNameExtracter,
      final Function<String, String> shapeNameExtracter) {
    final List<ASTFunctionCall> i_sumCalls = OdeTransformer.get_sumFunctionCalls(body.getODEBlock().get());

    final List<ASTDeclaration> pscInitialValues = solverOutput.initial_values
        .stream()
        .map(initialValue -> initialValue.getKey() + " real")
        .map(AstCreator::createDeclaration)
        .collect(toList());

    for (final ASTDeclaration pscInitialValueDeclaration:pscInitialValues) {
      final String pscInitialValue = pscInitialValueDeclaration.getVars().get(0);

      final String shapeName = shapeNameExtracter.apply(pscInitialValue);
      final String shapeStateVariable = stateVariableNameExtracter.apply(pscInitialValue);

      for (ASTFunctionCall i_sum_call:i_sumCalls) {
        final String shapeNameInCall = AstUtils.toString(i_sum_call.getArgs().get(0));
        if (shapeNameInCall.equals(shapeName)) {
          final String bufferName = AstUtils.toString(i_sum_call.getArgs().get(1));
          final ASTAssignment pscUpdateStep = createAssignment(
              shapeStateVariable + " += " +  pscInitialValue + " * "+ bufferName);
          addAssignmentToDynamics(pscUpdateStep, body);
        }

      }

    }

  }

  void addAssignmentToDynamics(
      final ASTAssignment astAssignment, final ASTBody astBody) {
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();

    astStmt.setSmall_Stmt(astSmall_stmt);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(astAssignment);

    astBody.getDynamics().get(0).getBlock().getStmts().add(astStmt);
  }

  ASTStmt statement(final ASTAssignment astAssignment) {
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    astSmall_stmt.setAssignment(astAssignment);
    astStmt.setSmall_Stmt(astSmall_stmt);
    return astStmt;
  }

}
