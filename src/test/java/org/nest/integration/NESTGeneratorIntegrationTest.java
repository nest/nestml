/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import com.google.common.collect.Lists;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.GenerationTest;

import java.io.IOException;
import java.util.List;

/**
 * Test the entire generation pipeline without mocks
 *
 * @author plotnikov
 */
public class NESTGeneratorIntegrationTest extends GenerationTest {
  private final List<String> pscModelsWithOde = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron_ode.nestml"
  );

  private final List<String> nestmlPSCModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron.nestml",
      "src/test/resources/codegeneration/iaf_tum_2000.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp.nestml",
      "src/test/resources/codegeneration/iaf_psc_delta.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp_multisynapse.nestml",
      "src/test/resources/codegeneration/mat2_psc_exp.nestml",
      "src/test/resources/codegeneration/izhikevich.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_multisynapse.nestml"
  );

  private final List<String> nestmlCondModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_cond_alpha.nestml"
  );

  private final List<String> nestmlCondModelExplicit = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_cond_alpha_implicit.nestml"
  );

  private final List<String> workshopModels = Lists.newArrayList(
      "src/test/resources/codegeneration/workshop.nestml"
  );

  private final List<String> blueGene = Lists.newArrayList(
      "src/test/resources/codegeneration/bluegene/aeif_cond_alpha_neuron.nestml",
      "src/test/resources/codegeneration/bluegene/hh_cond_alpha.nestml"
  );

  @Ignore
  @Test
  public void testFeedbackModels() {
    workshopModels.forEach(this::checkCocos);
    workshopModels.forEach(this::invokeCodeGenerator);
  }

  @Test
  public void testModelsWithoutOde() throws IOException {
    nestmlPSCModels.forEach(this::checkCocos);
    nestmlPSCModels.forEach(this::invokeCodeGenerator);
  }

  @Ignore("Don't run this tests on github")
  @Test
  public void testPscModelWithOde() {
    pscModelsWithOde.forEach(this::checkCocos);
    pscModelsWithOde.forEach(this::invokeCodeGenerator);
  }

  @Ignore
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

}
