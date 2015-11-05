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
 */
public class GenerateNESTModelsTest extends GenerationTestBase {
  private static final String INTEGRATION_MODEL_PATH = "src/test/resources/integration";

  private static final String OUTPUT_FOLDER = "target";

  private final List<String> nestmlModels = Lists.newArrayList(
      "src/test/resources/integration/nest.nestml");

  @Override
  protected String getModelPath() {
    return INTEGRATION_MODEL_PATH;
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
