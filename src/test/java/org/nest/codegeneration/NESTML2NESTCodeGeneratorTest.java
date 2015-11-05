/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import com.google.common.collect.Lists;
import org.junit.Test;

import java.io.IOException;
import java.util.List;


/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 * @since 0.0.1
 */
public class NESTML2NESTCodeGeneratorTest extends GenerationTestBase {
  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private final List<String> nestmlModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron_module.nestml",
      //"src/test/resources/codegeneration/iaf_neuron_ode_module.nestml"
      "src/test/resources/codegeneration/iaf_tum_2000_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_delta_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp_multisynapse_module.nestml",
      "src/test/resources/codegeneration/mat2_psc_exp_module.nestml",
      "src/test/resources/codegeneration/izhikevich_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_multisynapse_module.nestml",
      "src/test/resources/codegeneration/iaf_cond_alpha_module.nestml"
  );

  @Override
  protected String getModelPath() {
    return TEST_MODEL_PATH;
  }

  @Test
  public void checkCocosOnModels() throws IOException {
    nestmlModels.forEach(this::checkCocos);
  }

  @Test
  public void testHeaderGenerator() throws IOException {
    nestmlModels.forEach(this::generateHeader);
  }

  @Test
  public void testImplementationGenerator() throws IOException {
    nestmlModels.forEach(this::generateClassImplementation);
  }

  @Test
  public void testGenerateCodeForModelIntegrationInNest() throws IOException {
    nestmlModels.forEach(this::generateCodeForModelIntegrationInNest);
  }


}
