/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Test;

import java.io.IOException;

/**
 * Runs the codegenerator and compiles the resulting code. Afterthat, check is the make commomand
 * run successfully.
 *
 * @author plotnikov
 * @since 0.0.2
 */
public class NESTMLCompilationTest {

  @Test
  public void testCompilationOfTheGeneratedCode() throws IOException {
    final String compilationCommand = "make";
    final Runtime runtime = Runtime.getRuntime();
    runtime.exec(compilationCommand);
  }

}
