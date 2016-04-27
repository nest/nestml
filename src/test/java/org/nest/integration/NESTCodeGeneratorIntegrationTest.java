/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Log;
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
      "src/test/resources/codegeneration/iaf_neuron.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp.nestml",
      "src/test/resources/codegeneration/iaf_tum_2000.nestml"
      // TODO "src/test/resources/codegeneration/iaf_psc_delta.nestml",
  );

  private final List<String> imperativeModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_tum_2000_imerative.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_imperative.nestml",
      //"src/test/resources/codegeneration/iaf_psc_exp_multisynapse.nestml",
      "src/test/resources/codegeneration/mat2_psc_exp.nestml",
      "src/test/resources/codegeneration/izhikevich.nestml"//,
      //"src/test/resources/codegeneration/iaf_psc_alpha_multisynapse.nestml"
  );

  private final List<String> nestmlCondModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_cond_alpha.nestml"
  );

  private final List<String> nestmlCondModelExplicit = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_cond_alpha_implicit.nestml"
  );

  private final List<String> blueGene = Lists.newArrayList(
      "src/test/resources/codegeneration/bluegene/aeif_cond_alpha_neuron.nestml",
      "src/test/resources/codegeneration/bluegene/hh_cond_alpha.nestml"
  );

  @Test
  public void testCocos() {
    pscModelsWithOde.forEach(this::checkCocos);
    imperativeModels.forEach(this::checkCocos);
    nestmlCondModels.forEach(this::checkCocos);
    nestmlCondModelExplicit.forEach(this::checkCocos);
    blueGene.forEach(this::checkCocos);
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

  @Ignore("Don't run this tests on github")
  @Test
  public void testPSCModelsWithOde() {
    Log.enableFailQuick(false);
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
  }

  @Test
  public void testImplicitForm() {
    nestmlCondModelExplicit.forEach(this::checkCocos);
    nestmlCondModelExplicit.forEach(this::invokeCodeGenerator);
  }

  @Test
  public void testBluegeneModels() {
    blueGene.forEach(this::checkCocos);
    blueGene.forEach(this::invokeCodeGenerator);
  }

  @Ignore("Don't run this tests on github")
  @Test
  public void testManually() {
    final List<String> modelName = Lists.newArrayList("src/test/resources/codegeneration/iaf_tum_2000.nestml");
    modelName.forEach(this::checkCocos);
    modelName.forEach(this::invokeCodeGenerator);
    final List<ASTNESTMLCompilationUnit> roots = modelName.stream()
        .map(this::parseAndBuildSymboltable)
        .collect(Collectors.toList());
    generateNESTModuleCode(roots);
  }

}