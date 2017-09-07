/*
 * SolverInputTest.java
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
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTOdeDeclaration;

import static org.junit.Assert.*;

/**
 *
 * @author plotnikov
 */
public class SolverInputTest extends ModelbasedTest {
  private static final String COND_MODEL_FILE_PATH = "models/iaf_cond_alpha.nestml";
  private static final String PSC_MODEL_FILE_PATH = "models/iaf_psc_alpha.nestml";
  private static final String DELTA_MODEL_FILE_PATH = "models/iaf_psc_delta.nestml";

  @Test
  public void test_cond_model() {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(COND_MODEL_FILE_PATH);

    final ASTOdeDeclaration odeBlock = root.getNeurons().get(0).getOdeBlock().get();
    SolverInput solverInput = new SolverInput(odeBlock);
    String result = solverInput.toJSON();
    System.out.println(result);
    assertNotNull(result);

  }

  @Test
  public void test_psc_model() {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(PSC_MODEL_FILE_PATH);

    final ASTOdeDeclaration odeBlock = root.getNeurons().get(0).getOdeBlock().get();
    SolverInput solverInput = new SolverInput(odeBlock);
    String result = solverInput.toJSON();
    System.out.println(result);
    assertNotNull(result);

  }

  @Test
  public void test_shapes_only() {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(PSC_MODEL_FILE_PATH);

    final ASTOdeDeclaration odeBlock = root.getNeurons().get(0).getOdeBlock().get();
    SolverInput solverInput = new SolverInput(odeBlock.getShapes());
    String result = solverInput.toJSON();
    System.out.println(result);
    assertNotNull(result);

  }

  @Test
  public void test_delta_shape() {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(DELTA_MODEL_FILE_PATH);

    final ASTOdeDeclaration odeBlock = root.getNeurons().get(0).getOdeBlock().get();
    SolverInput solverInput = new SolverInput(odeBlock);
    String result = solverInput.toJSON();
    System.out.println(result);
    assertNotNull(result);

  }

}