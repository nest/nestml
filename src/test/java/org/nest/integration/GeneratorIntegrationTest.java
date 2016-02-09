/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import com.google.common.collect.Lists;
import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.GenerationTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

/**
 * Test the entire generation pipeline without mocks
 *
 * @author plotnikov
 */
public class GeneratorIntegrationTest extends GenerationTestBase {
  private final List<String> pscModelsWithOde = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron_ode.nestml"
  );

  private final List<String> nestmlPSCModels = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_neuron.nestml"/*,
      "src/test/resources/codegeneration/iaf_tum_2000.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp.nestml",
      "src/test/resources/codegeneration/iaf_psc_delta.nestml",
      "src/test/resources/codegeneration/iaf_psc_exp_multisynapse.nestml",
      "src/test/resources/codegeneration/mat2_psc_exp.nestml",
      "src/test/resources/codegeneration/izhikevich.nestml",
      "src/test/resources/codegeneration/iaf_psc_alpha_multisynapse.nestml"*/
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

  private final List<String> blueGen = Lists.newArrayList(
      "src/test/resources/codegeneration/bluegene/aeif_cond_alpha_neuron.nestml",
      "src/test/resources/codegeneration/bluegene/hh_cond_alpha.nestml"
  );
  @Ignore
  @Test
  public void testFeedbackModels() {
    workshopModels.forEach(this::invokeCodeGenerator);
  }

  @Ignore
  @Test
  public void testWorkshopCode() {
    workshopModels.forEach(this::checkCocos);
    workshopModels.forEach(this::invokeCodeGenerator);
  }

  @Test
  public void checkCocosOnModels() throws IOException {
    nestmlPSCModels.forEach(this::checkCocos);
//    pscModelsWithOde.forEach(this::checkCocos);
//    nestmlCondModels.forEach(this::checkCocos);
  }

  @Test
  public void testModelsWithoutOde() throws IOException {
    nestmlPSCModels.forEach(this::invokeCodeGenerator);
  }

  @Ignore("Don't run this tests on github")
  @Test
  public void testPscModelWithOde() {
    pscModelsWithOde.forEach(this::invokeCodeGenerator);
  }

  @Ignore
  @Test
  public void testCondModel() {
    nestmlCondModels.forEach(this::invokeCodeGenerator);
  }

  @Test
  public void testImplicitForm() {
    nestmlCondModelExplicit.forEach(this::invokeCodeGenerator);

  }

  @Test
  public void testBluegenModels() {
    blueGen.forEach(this::checkCocos);
    blueGen.forEach(this::invokeCodeGenerator);

  }
}
