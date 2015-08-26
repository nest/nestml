/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

/**
 * TODO
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTML2NESTWithODECodeGeneratorTest extends GenerationTestBase {

  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String OUTPUT_FOLDER = "target";

  private final static String GENERATED_MATRIX_PATH = "src/test/resources/org/nest/ode/solution.matrix.tmp";

  @Override
  protected String getModelPath() {
    return TEST_MODEL_PATH;
  }
}
