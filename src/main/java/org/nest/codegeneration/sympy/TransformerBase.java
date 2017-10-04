package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.io.StringReader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

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
    declarationsFile.forEach(declaration -> addVariableToInitialValue(astNeuron, declaration));
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
      astNeuron.addToInitialValuesBlock(astDeclaration);

      return astNeuron;

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

  static void addDeclarationToUpdateBlock(final ASTDeclaration astDeclaration, final ASTNeuron astNeuron) {
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();

    astStmt.setSmall_Stmt(astSmall_stmt);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setDeclaration(astDeclaration);

    astNeuron.getUpdateBlocks().get(0).getBlock().getStmts().add(astStmt);
  }

  public static List<Map.Entry<String, String>> computeShapeStateVariablesWithInitialValues(SolverOutput solverOutput) {
    List<Map.Entry<String, String>> stateShapeVariablesWithInitialValues = Lists.newArrayList();

    for (final String shapeStateVariable : solverOutput.shape_state_variables) {
      for (Map.Entry<String, String> initialValue:solverOutput.initial_values) {
        if (initialValue.getKey().endsWith(shapeStateVariable)) {
          stateShapeVariablesWithInitialValues.add(new HashMap.SimpleEntry<>(shapeStateVariable, initialValue.getValue()));
        }

      }

    }
    return stateShapeVariablesWithInitialValues;
  }

  static void applyIncomingSpikes(final ASTNeuron astNeuron) {
    final List<ASTFunctionCall> convCalls = OdeTransformer.get_sumFunctionCalls(astNeuron);
    final ExpressionsPrettyPrinter printer = new ExpressionsPrettyPrinter();

    final List<ASTAssignment> spikesUpdates = Lists.newArrayList();
    for (ASTFunctionCall convCall:convCalls) {
      String shape = convCall.getArgs().get(0).getVariable().get().toString();
      String buffer = convCall.getArgs().get(1).getVariable().get().toString();

      // variables could be added during the current transformation and, therefore, are not a part of the AST now.
      // therefore they must be found on the AST level and not via SymbolTable
      for (ASTDeclaration astDeclaration:astNeuron.getInitialValuesDeclarations()) {
        for (ASTVariable variable:astDeclaration.getVars()) {
          if (variable.toString().matches(shape + "(')*") || // handwritten models
              variable.toString().matches(shape + "__\\d+$")) { // generated models
            if (!astDeclaration.getExpr().isPresent()) {
              System.out.println();
            }
            spikesUpdates.add(AstCreator.createAssignment(
                variable.toString() + " += " + buffer + " * " + printer.print(astDeclaration.getExpr().get())));
          }

        }

      }

    }
    spikesUpdates.forEach(update -> addAssignmentToUpdateBlock(update, astNeuron));
  }


  static void addAssignmentToUpdateBlock(final ASTAssignment astAssignment, final ASTNeuron astNeuron) {
    final ASTStmt astStmt = NESTMLNodeFactory.createASTStmt();
    final ASTSmall_Stmt astSmall_stmt = NESTMLNodeFactory.createASTSmall_Stmt();

    astStmt.setSmall_Stmt(astSmall_stmt);

    // Goal: add the y-assignments at the end of the expression
    astSmall_stmt.setAssignment(astAssignment);

    astNeuron.getUpdateBlocks().get(0).getBlock().getStmts().add(astStmt);
  }
}
