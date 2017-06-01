/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import org.junit.Before;
import org.junit.Test;
import org.nest.base.GenerationBasedTest;
import org.nest.mocks.CondMock;
import org.nest.mocks.PSCMock;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.utils.FilesHelper;

import static com.google.common.collect.Lists.newArrayList;

/**
 * Generates entire NEST implementation for several NESTML models. Uses MOCKs or works with models without ODEs.
 *
 * @author plotnikov
 */
public class NestCodeGeneratorTest extends GenerationBasedTest {
  private static final PSCMock pscMock = new PSCMock();
  private static final CondMock condMock  = new CondMock();

  private static final String PSC_MODEL_WITH_ODE = "models/iaf_psc_alpha.nestml";
  private static final String PSC_MODEL_IMPERATIVE = "src/test/resources/codegeneration/imperative/iaf_psc_alpha_imperative.nestml";
  private static final String PSC_MODEL_THREE_BUFFERS = "src/test/resources/codegeneration/iaf_psc_alpha_three_buffers.nestml";
  private static final String NEURON_WITH_SETTER = "src/test/resources/codegeneration/neuron_with_setter.nestml";
  private static final String COND_MODEL_WITH_ODE = "models/iaf_cond_alpha.nestml";

  @Before
  public void cleanUp() {
    FilesHelper.deleteFilesInFolder(CODE_GEN_OUTPUT);
  }

  @Test
  public void testPSCModelWithoutOde() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_IMPERATIVE);
    scopeCreator.runSymbolTableCreator(root);
    final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator, pscMock, true);

    generator.analyseAndGenerate(root, CODE_GEN_OUTPUT);
    generator.generateNESTModuleCode(newArrayList(root), MODULE_NAME, CODE_GEN_OUTPUT);
  }

  @Test
  public void testPSCModelWithOde() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_WITH_ODE);
    scopeCreator.runSymbolTableCreator(root);
    final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator, pscMock, true);

    generator.analyseAndGenerate(root, CODE_GEN_OUTPUT);
    generator.generateNESTModuleCode(newArrayList(root), MODULE_NAME, CODE_GEN_OUTPUT);
  }

  @Test
  public void testCondModelWithShapes() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(COND_MODEL_WITH_ODE);
    scopeCreator.runSymbolTableCreator(root);
    final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator, condMock, true);

    generator.analyseAndGenerate(root, CODE_GEN_OUTPUT);
    generator.generateNESTModuleCode(newArrayList(root), MODULE_NAME, CODE_GEN_OUTPUT);
  }

  @Test
  public void testPSCModelWithThreeBuffers() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_THREE_BUFFERS);
    scopeCreator.runSymbolTableCreator(root);
    final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator, pscMock, true);

    generator.analyseAndGenerate(root, CODE_GEN_OUTPUT);
    generator.generateNESTModuleCode(newArrayList(root), MODULE_NAME, CODE_GEN_OUTPUT);
  }

  @Test
  public void testNeuronWithSetter() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(NEURON_WITH_SETTER);
    scopeCreator.runSymbolTableCreator(root);
    final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator, pscMock, true);

    generator.analyseAndGenerate(root, CODE_GEN_OUTPUT);
    generator.generateNESTModuleCode(newArrayList(root), MODULE_NAME, CODE_GEN_OUTPUT);
  }
}
