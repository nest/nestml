/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;

import static org.junit.Assert.assertEquals;

/**
 * Iterates through good models and checks that there is no errors in log.
 *
 * @author plotnikov
 */
public class ASTBodyTest extends ModelbasedTest {
  private static final String PSC_MODEL_THREE_BUFFERS = "src/test/resources/codegeneration/iaf_psc_alpha_three_buffers.nestml";

  @Test
  public void getSameTypeBuffer() throws Exception {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(PSC_MODEL_THREE_BUFFERS);
    final ASTBody astBody = root.getNeurons().get(0).getBody();
    final List<VariableSymbol> buffers = astBody.getMultipleReceptors();
    assertEquals(3, buffers.size());

  }

  @Test
  public void getCurrentBuffer() {
    ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(PSC_MODEL_THREE_BUFFERS);
    final ASTBody astBody = root.getNeurons().get(0).getBody();
    final List<VariableSymbol> buffers = astBody.getCurrentBuffers();
    assertEquals(1, buffers.size());
  }

}