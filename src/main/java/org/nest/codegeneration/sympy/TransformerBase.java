package org.nest.codegeneration.sympy;

import de.monticore.ast.ASTNode;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.io.StringReader;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.AstCreator.createAssignment;
import static org.nest.codegeneration.sympy.AstCreator.createDeclaration;

/**
 * Provides common methods for AST transformations which are performed after SymPy analysis.
 *
 * @author plotnikov
 */
final public class TransformerBase {

  // example initial value iv__I_shape_in
  // example initial value iv__I_shape_in__1
  // the shape state variable is `I_shape_in__1`
  // the shape name is `I_shape_in`
  final static Function<String, String> variableNameExtracter = initialValue -> initialValue.substring("iv__".length());

  final static Function<String, String> shapeNameExtracter = initialValue -> {
    final String tmp = initialValue.substring("iv__".length());
    if (tmp.lastIndexOf("__") == -1) {
      return tmp;
    }
    else {
      return tmp.substring(0, tmp.lastIndexOf("__"));
    }
  };

  private static final NESTMLParser parser = new NESTMLParser();

  static ASTNeuron addVariablesToState(final ASTNeuron astNeuron, final List<String> shapeStateVariables) {

    //final List<String> correspondingShapeSymbols = shapeStateVariables
    //    .stream()
    //    .map(this::getShapeNameFromStateVariable)
    //    .collect(Collectors.toList());

    for (String shapeStateVariable : shapeStateVariables) {
      // final Scope scope = astNeuron.getEnclosingScope().get();
      //checkState(astNeuron.getEnclosingScope().isPresent());
      //final String vectorDatatype = correspondingShapeSymbols.get(i).isVector()?"[" + correspondingShapeSymbols.get(i).getVectorParameter().get() + "]":"";
      final String stateVarDeclaration = shapeStateVariable + " real";

      astNeuron.addToStateBlock(createDeclaration(stateVarDeclaration));
    }

    return astNeuron;
  }

  /**
   * Add a list with declarations to the internals block in the neuron.
   */
  static ASTNeuron addVariablesToInternals(
      final ASTNeuron astNeuron,
      final List<Map.Entry<String, String>> declarationsFile) {
    declarationsFile.forEach(declaration -> addVariableToInternals(astNeuron, declaration));
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  static ASTNeuron addVariableToInternals(
      final ASTNeuron astNeuron,
      final Map.Entry<String, String> declaration) {
    try {
      ASTExpr tmp = parser.parseExpr(new StringReader(declaration.getValue())).get(); // must not fail by construction
      final Optional<VariableSymbol> vectorVariable = AstUtils.getVectorizedVariable(tmp, astNeuron.getSpannedScope().get());

      final String declarationString = declaration.getKey() + " real" +
                                       vectorVariable.map(variableSymbol -> "[" + variableSymbol.getVectorParameter().get() + "]").orElse("")
                                       + " = " + declaration.getValue();
      final ASTDeclaration astDeclaration = parser.parseDeclaration(new StringReader(declarationString)).get();
      vectorVariable.ifPresent(var -> astDeclaration.setSizeParameter(var.getVectorParameter().get()));
      astNeuron.addToInternalBlock(astDeclaration);
      return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Must not fail by construction.");
    }

  }


  /**
   * Add a list with declarations to the internals block in the neuron.
   */
  static ASTNeuron addVariablesToInitialValues(
      final ASTNeuron astNeuron,
      final List<Map.Entry<String, String>> declarationsFile) {
    declarationsFile.forEach(declaration -> addVariableToInternals(astNeuron, declaration));
    return astNeuron;
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   */
  static ASTNeuron addVariableToInitialValue(
      final ASTNeuron astNeuron,
      final Map.Entry<String, String> declaration) {
    try {
      ASTExpr tmp = parser.parseExpr(new StringReader(declaration.getValue())).get(); // must not fail by construction
      final Optional<VariableSymbol> vectorVariable = AstUtils.getVectorizedVariable(tmp, astNeuron.getSpannedScope().get());

      final String declarationString = declaration.getKey() + " real" +
                                       vectorVariable.map(variableSymbol -> "[" + variableSymbol.getVectorParameter().get() + "]").orElse("")
                                       + " = " + declaration.getValue();
      final ASTDeclaration astDeclaration = parser.parseDeclaration(new StringReader(declarationString)).get();
      vectorVariable.ifPresent(var -> astDeclaration.setSizeParameter(var.getVectorParameter().get()));
      //astNeuron.addToInitialValuesBlock(astDeclaration);
      throw new RuntimeException();
      //return astNeuron;
    }
    catch (IOException e) {
      throw new RuntimeException("Must not fail by construction.");
    }

  }


  static ASTNeuron replaceIntegrateCallThroughPropagation(final ASTNeuron astNeuron, List<String> propagatorSteps) {
    // It must work for multiple integrate calls!
    final Optional<ASTFunctionCall> integrateCall = AstUtils.getFunctionCall(
        PredefinedFunctions.INTEGRATE_ODES,
        astNeuron.getUpdateBlocks().get(0));

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
          TransformerBase.class.getSimpleName());
      return astNeuron;
    }

  }

  /**
   * Add updates of state variables with the PSC initial value and corresponding inputs from buffers.
   */
  static void addShapeVariableUpdatesWithIncomingSpikes(
      final SolverOutput solverOutput,
      final ASTNeuron body,
      final Function<String, String> stateVariableNameExtracter,
      final Function<String, String> shapeNameExtracter) {
    final List<ASTFunctionCall> i_sumCalls = OdeTransformer.get_sumFunctionCalls(body.findEquationsBlock().get());

    final List<ASTDeclaration> pscInitialValues = solverOutput.initial_values
        .stream()
        .map(initialValue -> initialValue.getKey() + " real")
        .map(AstCreator::createDeclaration)
        .collect(toList());

    for (final ASTDeclaration pscInitialValueDeclaration:pscInitialValues) {
      final String pscInitialValue = pscInitialValueDeclaration.getVars().get(0).toString();

      final String shapeName = shapeNameExtracter.apply(pscInitialValue);
      final String shapeStateVariable = stateVariableNameExtracter.apply(pscInitialValue);

      for (ASTFunctionCall i_sum_call:i_sumCalls) {
        final String shapeNameInCall = AstUtils.toString(i_sum_call.getArgs().get(0));
        if (shapeNameInCall.equals(shapeName)) {
          final String bufferName = AstUtils.toString(i_sum_call.getArgs().get(1));
          final ASTAssignment pscUpdateStep = createAssignment(
              shapeStateVariable + " += " +  pscInitialValue + " * "+ bufferName);
          addAssignmentToUpdateBlock(pscUpdateStep, body);
        }

      }

    }

  }

  static void addAssignmentToUpdateBlock(final ASTAssignment astAssignment, final ASTNeuron astNeuron) {
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();

    astStmt.setSmall_Stmt(astSmall_stmt);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(astAssignment);

    astNeuron.getUpdateBlocks().get(0).getBlock().getStmts().add(astStmt);
  }

  static void addDeclarationToUpdateBlock(final ASTDeclaration astDeclaration, final ASTNeuron astNeuron) {
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();

    astStmt.setSmall_Stmt(astSmall_stmt);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setDeclaration(astDeclaration);

    astNeuron.getUpdateBlocks().get(0).getBlock().getStmts().add(astStmt);
  }

  static ASTNeuron removeShapes(ASTNeuron astNeuron) {
    astNeuron.findEquationsBlock().get().getShapes().clear();
    return astNeuron;
  }

}
