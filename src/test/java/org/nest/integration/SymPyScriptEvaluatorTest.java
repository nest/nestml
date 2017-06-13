/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.codegeneration.sympy.SolverFrameworkGenerator;
import org.nest.codegeneration.sympy.SymPyScriptEvaluator;
import org.nest.codegeneration.sympy.TransformerBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTOdeDeclaration;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.utils.FilesHelper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Test evaluation of the solver script. Depends on successful script generation.
 *
 * @author plonikov
 */
public class SymPyScriptEvaluatorTest extends ModelbasedTest {
  private static final String IAF_PSC_EXP = "models/iaf_psc_exp.nestml";
  private static final String IAF_PSC_ALPHA = "models/iaf_psc_alpha.nestml";
  private static final String PSC_MODEL_FILE = "models/iaf_neuron.nestml";
  private static final String COND_MODEL_FILE = "models/iaf_cond_alpha.nestml";

  private static final Path SYMPY_OUTPUT = Paths.get(OUTPUT_FOLDER.toString(), "sympy");

  @Test
  public void testPSC_ALPHA_MODEL_new_api() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> root = parser.parse(IAF_PSC_ALPHA);
    assertTrue(root.isPresent());

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    FilesHelper.deleteFilesInFolder(SYMPY_OUTPUT);

    final SymPyScriptEvaluator symPyScriptEvaluator = new SymPyScriptEvaluator();
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinter.Builder.build();
    final ASTOdeDeclaration astOdeDeclaration =  root.get().getNeurons().get(0).getBody().getODEBlock().get();

    final List<String> shapes = astOdeDeclaration.getShapes()
        .stream()
        .map(prettyPrinter::printShape)
        .collect(Collectors.toList());
    final List<String> functions = astOdeDeclaration.getOdeFunctions()
        .stream()
        .map(prettyPrinter::printODEAlias)
        .collect(Collectors.toList());
    final List<String> odes = astOdeDeclaration.getODEs()
        .stream()
        .map(prettyPrinter::printEquation)
        .collect(Collectors.toList());

    symPyScriptEvaluator.solveOdeWithShapes(odes.get(0), shapes, SYMPY_OUTPUT);
  }

  @Test
  public void testPSC_ALPHA_MODEL() throws IOException {
    generateAndEvaluate(IAF_PSC_ALPHA);
  }

  @Test
  public void testPSC_EXP_MODEL() throws IOException {
    generateAndEvaluate(IAF_PSC_EXP);
  }

  @Test
  public void testIAF_NEURON() throws IOException {
    generateAndEvaluate(PSC_MODEL_FILE);
  }

  @Test
  public void testIAF_COND_ALPHA() throws IOException {
    generateAndEvaluate(COND_MODEL_FILE);
  }

  private void generateAndEvaluate(final String pathToModel) throws IOException {
    final Optional<ASTNESTMLCompilationUnit> root = parser.parse(pathToModel);
    assertTrue(root.isPresent());

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    FilesHelper.deleteFilesInFolder(SYMPY_OUTPUT);

    final String generatedScript = SolverFrameworkGenerator.generateExactSolverCommand(
        root.get().getNeurons().get(0));

    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();

    assertTrue(evaluator.evaluateCommand(generatedScript, SYMPY_OUTPUT));

    assertTrue(Files.exists(Paths.get(
        SYMPY_OUTPUT.toString(),
        root.get().getNeurons().get(0).getName() + "." + TransformerBase.SOLVER_TYPE)));
  }

}
