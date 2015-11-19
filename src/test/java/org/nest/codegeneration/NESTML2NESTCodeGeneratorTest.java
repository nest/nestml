/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import com.google.common.collect.Lists;
import org.junit.Ignore;
import org.junit.Test;

import java.io.IOException;
import java.util.List;


/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 */
public class NESTML2NESTCodeGeneratorTest extends GenerationTestBase {

  private final List<String> nestmlModelsWithOde = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml"
  );

  private final List<String> nestmlPSCModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron_module.nestml",
      "src/test/resources/codegeneration/iaf_tum_2000_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_delta_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp_multisynapse_module.nestml",
      "src/test/resources/codegeneration/mat2_psc_exp_module.nestml",
      "src/test/resources/codegeneration/izhikevich_module.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_multisynapse_module.nestml"
  );

  private final List<String> nestmlCondModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_cond_alpha_module.nestml"
  );


  @Test
  public void checkCocosOnModels() throws IOException {
    nestmlPSCModels.forEach(this::checkCocos);
    nestmlModelsWithOde.forEach(this::checkCocos);
    nestmlCondModels.forEach(this::checkCocos);
  }

  @Test
  public void testGenerator() throws IOException {
    nestmlPSCModels.forEach(this::invokeCodeGenerator);
  }

  @Ignore
  @Test
  public void testModelsWithOde() {
    nestmlModelsWithOde.forEach(this::generateCodeForNESTMLWithODE);
  }

  @Ignore
  @Test
  public void testCondModel() {
    nestmlCondModels.forEach(this::handleCondModel);
  }

}
