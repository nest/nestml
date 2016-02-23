/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.nio.file.Paths;

/**
 * Tests that the generator correctly handles a model with aliases
 * @author plotnikov
 */
public class AliasSolverScriptGeneratorTest extends ModelbasedTest {
  public static final String PATH_TO_PSC_MODEL
      = "src/test/resources/codegeneration/iaf_neuron.nestml";
  private final AliasSolverScriptGenerator aliasSolverGenerator = new AliasSolverScriptGenerator();

  @Test
  public void testGenerateAliasInverter() throws Exception {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PATH_TO_PSC_MODEL);
    scopeCreator.runSymbolTableCreator(root);
    aliasSolverGenerator.generateAliasInverter(
        root.getNeurons().get(0), Paths.get("target"));
  }

}