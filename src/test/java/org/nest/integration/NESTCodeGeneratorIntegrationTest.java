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
public class NESTCodeGeneratorIntegrationTest extends GenerationBasedTest {

  private final List<String> pscModelsWithOde = Lists.newArrayList(
      "models/iaf_neuron.nestml",
      "models/iaf_psc_alpha.nestml",
      "models/iaf_psc_exp.nestml",
      "models/iaf_tum_2000.nestml",
      "models/iaf_psc_delta.nestml",
      "models/mat2_psc_exp.nestml"
  );

  private final List<String> multisynapseModels = Lists.newArrayList(
      "models/iaf_psc_alpha_multisynapse.nestml",
      "models/iaf_psc_exp_multisynapse.nestml"
  );

  private final List<String> imperativeModels = Lists.newArrayList(
      "src/test/resources/codegeneration/imperative/iaf_tum_2000_imerative.nestml",
      "src/test/resources/codegeneration/imperative/iaf_psc_alpha_multisynapse_imperative.nestml",
      "src/test/resources/codegeneration/imperative/iaf_psc_delta_imperative.nestml",
      "src/test/resources/codegeneration/imperative/iaf_psc_exp_imperative.nestml",
      "src/test/resources/codegeneration/imperative/iaf_psc_exp_multisynapse_imperative.nestml",
      "src/test/resources/codegeneration/imperative/iaf_tum_2000_imerative.nestml",
      "src/test/resources/codegeneration/imperative/mat2_psc_exp_imperative.nestml"
  );

  private final List<String> nestmlCondModels = Lists.newArrayList(
      "models/iaf_cond_alpha.nestml"
  );

  private final List<String> nestmlCondImplicitModels = Lists.newArrayList(
      "models/iaf_cond_alpha_implicit.nestml",
      "models/iaf_cond_exp_implicit.nestml",
      "models/aeif_cond_alpha_implicit.nestml",
      "models/aeif_cond_exp_implicit.nestml",
      "models/hh_psc_alpha.nestml"

  );

  private final List<String> glf = Lists.newArrayList(
      "src/test/resources/codegeneration/gif/glif.nestml",
      "src/test/resources/codegeneration/gif/glif_2.nestml",
      "src/test/resources/codegeneration/gif/glif_extended.nestml"

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

  @Ignore("Doesn't work at the moments")
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


  @Ignore("Don't run this tests on github")
  @Test
  public void testGlifModel() {
    glf.forEach(this::checkCocos);
    glf.forEach(this::invokeCodeGenerator);
  }

  @Test
  public void testIzhikevich() {
    final List<String> modelName = Lists.newArrayList("models/izhikevich.nestml");
    modelName.forEach(this::checkCocos);
    modelName.forEach(this::invokeCodeGenerator);
    final List<ASTNESTMLCompilationUnit> roots = modelName.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

  @Ignore("Don't run this tests on github")
  @Test
  public void testManually() {
    final List<String> modelName = Lists.newArrayList("models/iaf_chxk_2008_implicit.nestml");
    modelName.forEach(this::checkCocos);
    modelName.forEach(this::invokeCodeGenerator);
    final List<ASTNESTMLCompilationUnit> roots = modelName.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

}