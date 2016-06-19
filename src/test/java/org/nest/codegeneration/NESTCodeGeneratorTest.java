/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import org.junit.Assert;
import org.junit.Test;
import org.nest.base.GenerationBasedTest;
import org.nest.codegeneration.helpers.AliasInverter;
import org.nest.commons._ast.ASTExpr;
import org.nest.mocks.PSCMock;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;
import org.nest.utils.FilesHelper;

import java.nio.file.Path;
import java.nio.file.Paths;

import static com.google.common.collect.Lists.newArrayList;

/**
 * Generates entire NEST implementation for several NESTML models. Uses MOCKs or works with models without ODEs.
 *
 * @author plotnikov
 */
public class NESTCodeGeneratorTest extends GenerationBasedTest {
  private static final Path OUTPUT_DIRECTORY = Paths.get("target", "build");
  private static final PSCMock pscMock = new PSCMock();

  private static final String PSC_MODEL_WITH_ODE = "src/test/resources/codegeneration/iaf_psc_alpha.nestml";
  private static final String PSC_MODEL_IMPERATIVE = "src/test/resources/codegeneration/imperative/iaf_psc_alpha_imperative.nestml";
  private static final String COND_MODEL_IMPLICIT = "src/test/resources/codegeneration/iaf_cond_alpha_implicit.nestml";

  @Test
  public void testPSCModelWithoutOde() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_IMPERATIVE);
    scopeCreator.runSymbolTableCreator(root);
    final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator, pscMock);
    final Path outputFolder = Paths.get(OUTPUT_DIRECTORY.toString(), "simple_psc");

    FilesHelper.deleteFilesInFolder(outputFolder);
    generator.analyseAndGenerate(root, outputFolder);
    generator.generateNESTModuleCode(newArrayList(root), "simple_psc", outputFolder);
  }

  @Test
  public void testPSCModelWithOde() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_WITH_ODE);
    scopeCreator.runSymbolTableCreator(root);
    final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator, pscMock);
    Path outputFolder = Paths.get(OUTPUT_DIRECTORY.toString(), "psc");

    FilesHelper.deleteFilesInFolder(outputFolder);
    generator.analyseAndGenerate(root, outputFolder);
    generator.generateNESTModuleCode(newArrayList(root), "psc", outputFolder);
  }

  @Test
  public void testCondModelWithImplicitOdes() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(COND_MODEL_IMPLICIT);
    scopeCreator.runSymbolTableCreator(root);
    final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator, pscMock);
    Path outputFolder = Paths.get(OUTPUT_DIRECTORY.toString(), "cond");

    FilesHelper.deleteFilesInFolder(outputFolder);
    generator.analyseAndGenerate(root, outputFolder);
    generator.generateNESTModuleCode(newArrayList(root), "cond", outputFolder);
  }


}
