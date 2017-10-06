/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.List;

import static org.junit.Assert.assertEquals;

/**
 * Iterates through good models and checks that there is no errors in log.
 *
 * @author plotnikov
 */
public class ASTNeuronTest extends ModelbasedTest {
  private static final String PSC_MODEL_THREE_BUFFERS = "src/test/resources/codegeneration/iaf_psc_alpha_three_buffers.nestml";

  @Test
  public void getSameTypeBuffer() throws Exception {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(PSC_MODEL_THREE_BUFFERS);
    final ASTNeuron astNeuron = root.getNeurons().get(0);
    final List<VariableSymbol> buffers = astNeuron.getMultipleReceptors();
    assertEquals(3, buffers.size());

  }

  @Test
  public void getCurrentBuffer() {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(PSC_MODEL_THREE_BUFFERS);
    final ASTNeuron astNeuron = root.getNeurons().get(0);
    final List<VariableSymbol> buffers = astNeuron.getCurrentBuffers();
    assertEquals(3, buffers.size()); //3 because the sppike buffers that have been declared as pA also count as CurrentBuffers
  }

}