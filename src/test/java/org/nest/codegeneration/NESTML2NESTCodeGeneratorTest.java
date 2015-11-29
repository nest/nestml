/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import com.google.common.collect.Lists;
import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 */
public class NESTML2NESTCodeGeneratorTest extends GenerationTestBase {

  private final List<String> pscModelsWithOde = Lists.newArrayList(
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

  private final List<String> nestmlCondModelExplicit = Lists.newArrayList(
      "src/test/resources/codegeneration/iaf_cond_alpha_implicit_module.nestml"
  );


  @Test
  public void checkCocosOnModels() throws IOException {
    nestmlPSCModels.forEach(this::checkCocos);
    pscModelsWithOde.forEach(this::checkCocos);
    nestmlCondModels.forEach(this::checkCocos);
  }

  @Test
  public void testGenerator() throws IOException {
    nestmlPSCModels.forEach(this::invokeCodeGenerator);
  }

  @Test
  public void testPscModelWithOde() {
    pscModelsWithOde.forEach(this::generateCodeForPSCModel);
  }

  @Ignore
  @Test
  public void testCondModel() {
    nestmlCondModels.forEach(this::generateNESTMLImplementation);
  }

  @Test
  public void testImplicitForm() {
    nestmlCondModelExplicit.forEach(this::generateNESTMLImplementation);
    for (final String model:nestmlCondModelExplicit) {
      final ASTNESTMLCompilationUnit root = parseNESTMLModel(model);
      scopeCreator.runSymbolTableCreator(root);
      Optional<ASTOdeDeclaration> odeDeclaration = ASTNodes.getAny(root, ASTOdeDeclaration.class);
      Assert.assertTrue(odeDeclaration.isPresent());

      generator.generateNESTCode(root, Paths.get("target"));
    }
  }

}
