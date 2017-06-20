/*
 * ASTNESTMLCompilationUnitTest.java
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

package org.nest.nestml._ast;

import org.junit.Assert;
import org.junit.Test;
import org.nest.base.ModelbasedTest;

/**
 * Tests handwritten extensions of the AST class.
 *
 * @author plotnikov
 */
public class ASTNESTMLCompilationUnitTest extends ModelbasedTest {
  private static final String TESTANT_MODEL = "src/test/resources/org/nest/nestml/_ast/file_with_two_neurons.nestml";

  @Test
  public void getNeuronNameAtLine() throws Exception {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(TESTANT_MODEL);
    Assert.assertEquals(ASTNESTMLCompilationUnit.NEURON_UNDEFINED_AT_LINE, root.getNeuronNameAtLine(0));
    Assert.assertEquals(ASTNESTMLCompilationUnit.NEURON_UNDEFINED_AT_LINE, root.getNeuronNameAtLine(-1));
    Assert.assertEquals("A", root.getNeuronNameAtLine(1));
    Assert.assertEquals("A", root.getNeuronNameAtLine(2));
    Assert.assertEquals("B", root.getNeuronNameAtLine(4));
    Assert.assertEquals("B", root.getNeuronNameAtLine(5));
    Assert.assertEquals(ASTNESTMLCompilationUnit.NEURON_UNDEFINED_AT_LINE, root.getNeuronNameAtLine(6));
  }

}