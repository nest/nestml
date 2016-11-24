/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import com.google.common.collect.Lists;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.GenerationBasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Test the entire generation pipeline without mocks
 *
 * @author plotnikov
 */
public class NestCodeGeneratorIntegrationTest extends GenerationBasedTest {

  private final List<String> pscModelsWithOde = Lists.newArrayList(
      "models/iaf_psc_alpha.nestml",
      "models/iaf_psc_exp.nestml"
  );

  private final List<String> multisynapseModels = Lists.newArrayList(
      "models/iaf_psc_alpha_multisynapse.nestml",
      "models/iaf_psc_exp_multisynapse.nestml"
  );

  private final List<String> imperativeModels = Lists.newArrayList(
      "src/test/resources/codegeneration/imperative/iaf_psc_exp_imperative.nestml",
      "src/test/resources/codegeneration/imperative/mat2_psc_exp_imperative.nestml"
  );

  private final List<String> nestmlCondModels = Lists.newArrayList(
      "models/iaf_cond_alpha.nestml",
      "models/iaf_cond_exp.nestml",
      "models/aeif_cond_alpha.nestml"
  );

  private final List<String> nestmlCondImplicitModels = Lists.newArrayList(
      "models/iaf_cond_alpha_implicit.nestml"
  );

  @Test
  public void testCocos() {
    pscModelsWithOde.forEach(this::checkCocos);
    imperativeModels.forEach(this::checkCocos);
    nestmlCondModels.forEach(this::checkCocos);
    nestmlCondImplicitModels.forEach(this::checkCocos);
  }

  @Test
  public void testModelsWithoutOde() throws IOException {
    imperativeModels.forEach(this::checkCocos);
    imperativeModels.forEach(this::invokeCodeGenerator);
    final List<ASTNESTMLCompilationUnit> roots = imperativeModels.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

  @Test
  public void testMultisynapseModels() throws IOException {
    multisynapseModels.forEach(this::checkCocos);
    multisynapseModels.forEach(this::invokeCodeGenerator);
    final List<ASTNESTMLCompilationUnit> roots = multisynapseModels.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

  @Test
  public void testPSCModelsWithOde() {
    pscModelsWithOde.forEach(this::checkCocos);
    pscModelsWithOde.forEach(this::invokeCodeGenerator);

    final List<ASTNESTMLCompilationUnit> roots = pscModelsWithOde.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());

    generateNESTModuleCode(roots);
  }

  @Test
  public void testCondModel() {
    nestmlCondModels.forEach(this::checkCocos);
    nestmlCondModels.forEach(this::invokeCodeGenerator);

    final List<ASTNESTMLCompilationUnit> roots = nestmlCondModels.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

  @Ignore
  @Test
  public void testCondImplicitForm() {
    nestmlCondImplicitModels.forEach(this::checkCocos);
    nestmlCondImplicitModels.forEach(this::invokeCodeGenerator);

    final List<ASTNESTMLCompilationUnit> roots = nestmlCondImplicitModels.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

}