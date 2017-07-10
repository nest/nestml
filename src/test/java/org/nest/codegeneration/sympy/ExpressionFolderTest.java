/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTAssignment;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.io.IOException;
import java.io.StringReader;
import java.util.List;
import java.util.Optional;

import static com.google.common.collect.Lists.newArrayList;
import static java.util.stream.Collectors.toList;
import static org.junit.Assert.assertTrue;

/**
 *
 */
public class ExpressionFolderTest extends ModelbasedTest {
  private static final ExpressionsPrettyPrinter printer = new ExpressionsPrettyPrinter();
  private static final String MODEL_FILE_PATH = "models/iaf_psc_alpha.nestml";

  @Test
  public void testExpressionFolding() throws IOException {
    final String expression = "(h*y1_I_shape_in + y2_I_shape_in)*exp(-h/tau_syn_in)";
    final NESTMLParser parser = new NESTMLParser();

    Optional<ASTExpr> ast = parser.parseExpr(new StringReader(expression));
    assertTrue(ast.isPresent());
    final ExpressionFolder expressionFolder = new ExpressionFolder();
    expressionFolder.fold(
        ast.get(),
        newArrayList("y1_I_shape_in", "y2_I_shape_in", "y1_I_shape_ex","y2_I_shape_ex")
    );
    System.out.println(printer.print(ast.get()));
  }

  @Test
  public void testAnother() throws IOException {
    final String expression = "y1_I_shape_in*exp(-h/tau_syn_in)";
    final NESTMLParser parser = new NESTMLParser();

    Optional<ASTExpr> ast = parser.parseExpr(new StringReader(expression));
    assertTrue(ast.isPresent());

    final ExpressionFolder expressionFolder = new ExpressionFolder();
    expressionFolder.fold(
        ast.get(),
        newArrayList("y1_I_shape_in", "y2_I_shape_in", "y1_I_shape_ex","y2_I_shape_ex")
    );
    System.out.println(printer.print(ast.get()));
  }

  @Test
  public void testFoldingPipeline() throws IOException {
    final ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(MODEL_FILE_PATH);
    final ASTNeuron neuron = root.getNeurons().get(0);
    final SolverOutput solverOutput = SolverOutput.fromJSON(SolverJsonData.IAF_PSC_ALPHA);

    final List<String> stateVariableNames = newArrayList();
    stateVariableNames.addAll(neuron.getBody().getStateSymbols()
        .stream()
        .map(VariableSymbol::getName)
        .collect(toList()));

    stateVariableNames.addAll(solverOutput.shape_state_variables);

    final List<String> stateUpdates = solverOutput.updates_to_shape_state_variables
        .stream().map(e -> e.getKey() + " = " + e.getValue())
        .collect(toList());

    final List<ASTAssignment> stateUpdateAssignments = stateUpdates
        .stream()
        .map(AstCreator::createAssignment)
        .collect(toList());

    final List<ASTExpr> rhsExpressions = stateUpdateAssignments
        .stream()
        .map(ASTAssignment::getExpr)
        .collect(toList());

    for (final ASTExpr expr:rhsExpressions) {
      final ExpressionFolder expressionFolder = new ExpressionFolder();
      expressionFolder.fold(expr, stateVariableNames);
      System.out.println(new ExpressionsPrettyPrinter().print(expr));
      //assertTrue(expressionFolder.getInternalVariables().size() == 1);

    }

  }

}
