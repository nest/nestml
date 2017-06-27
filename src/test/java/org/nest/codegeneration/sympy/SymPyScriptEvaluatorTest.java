/*
 * SymPyScriptEvaluatorTest.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.codegeneration.sympy.SolverFrameworkGenerator;
import org.nest.codegeneration.sympy.SolverOutput;
import org.nest.codegeneration.sympy.SymPyScriptEvaluator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTOdeDeclaration;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.FilesHelper;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
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

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator();
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    FilesHelper.deleteFilesInFolder(SYMPY_OUTPUT);

    final SymPyScriptEvaluator symPyScriptEvaluator = new SymPyScriptEvaluator();
    final ASTOdeDeclaration astOdeDeclaration =  root.get().getNeurons().get(0).getBody().getODEBlock().get();

    final SolverOutput testant = symPyScriptEvaluator.solveOdeWithShapes(astOdeDeclaration, SYMPY_OUTPUT);
    assertEquals("success", testant.status);
    assertEquals("exact", testant.solver);
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

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator();
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    FilesHelper.deleteFilesInFolder(SYMPY_OUTPUT);

    final String generatedScript = SolverFrameworkGenerator.generateExactSolverCommand(
        root.get().getNeurons().get(0));

    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();

    assertTrue(evaluator.evaluateCommand(generatedScript, SYMPY_OUTPUT));

    // TODO
    /*assertTrue(Files.exists(Paths.get(
        SYMPY_OUTPUT.toString(),
        root.get().getNeurons().get(0).getName() + "." + TransformerBase.SOLVER_TYPE)));*/
  }

}
