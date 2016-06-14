package org.nest.codegeneration.sympy;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTSimple_Stmt;
import org.nest.spl._ast.ASTSmall_Stmt;
import org.nest.spl._ast.SPLNodeFactory;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;
import static org.nest.codegeneration.sympy.NESTMLASTCreator.createAliases;
import static org.nest.utils.ASTUtils.getVectorizedVariable;

/**
 * Provides common methods for solver transformations.
 *
 * @author plotnikov
 */
class TransformerBase {
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
  ASTNeuron addDeclarationsInternalBlock(
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

    pscInitialValues.stream().forEach(initialValue -> astNeuron.getBody().addToInternalBlock(initialValue));

    return astNeuron;
  }
  ASTNeuron replaceODEPropagationStep(final ASTNeuron astNeuron, final Path updateStepFile) {
    try {
    final List<ASTSmall_Stmt> propagatorSteps = Files.lines(updateStepFile)
        .map(NESTMLASTCreator::createAssignment)
        .map(this::smallStatement)
        .collect(toList());
      return replaceODEPropagationStep(astNeuron, propagatorSteps);

    } catch (IOException e) {
      throw new RuntimeException("Cannot parse assignment statement.", e);
    }
  }

  ASTNeuron replaceODEPropagationStep(final ASTNeuron astNeuron, List<ASTSmall_Stmt> propagatorSteps) {

    final ASTBody astBodyDecorator = astNeuron.getBody();

    // It must work for multiple integrate calls!
    final Optional<ASTFunctionCall> integrateCall = ASTUtils.getFunctionCall(
        PredefinedFunctions.INTEGRATE,
        astBodyDecorator.getDynamics().get(0));

    if (integrateCall.isPresent()) {
      final Optional<ASTNode> smallStatement = ASTUtils.getParent(integrateCall.get(), astNeuron);
      checkState(smallStatement.isPresent());
      checkState(smallStatement.get() instanceof ASTSmall_Stmt);
      final ASTSmall_Stmt integrateCallStatement = (ASTSmall_Stmt) smallStatement.get();

      final Optional<ASTNode> simpleStatement = ASTUtils.getParent(smallStatement.get(), astNeuron);
      checkState(simpleStatement.isPresent());
      checkState(simpleStatement.get() instanceof ASTSimple_Stmt);
      final ASTSimple_Stmt astSimpleStatement = (ASTSimple_Stmt) simpleStatement.get();
      int integrateFunction = astSimpleStatement.getSmall_Stmts().indexOf(integrateCallStatement);
      astSimpleStatement.getSmall_Stmts().remove(integrateCallStatement);
      astSimpleStatement.getSmall_Stmts().addAll(integrateFunction, propagatorSteps);

      return astNeuron;
    } else {
      Log.warn("The model has defined an ODE. But its solution is not used in the update state.");
      return astNeuron;
    }


  }

  ASTSmall_Stmt smallStatement(final ASTAssignment astAssignment) {
    final ASTSmall_Stmt astSmall_stmt = SPLNodeFactory.createASTSmall_Stmt();
    astSmall_stmt.setAssignment(astAssignment);
    return astSmall_stmt;
  }

}
