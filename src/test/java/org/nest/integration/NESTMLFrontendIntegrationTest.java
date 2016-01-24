/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Ignore;
import org.junit.Test;
import org.nest.cli.NESTMLFrontend;

import java.nio.file.Paths;

/**
 * TODO
 *
 * @author plotnikov
 */
@Ignore("Don't run this tests on github")
public class NESTMLFrontendIntegrationTest {
  private final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();

  @Test
  public void testRun() {
    nestmlFrontend.handleConsoleArguments(new String[] {
        "src/test/resources/codegeneration/iaf_neuron_ode.nestml",
        "--target", Paths.get("target","tmpOutput").toString()});
  }
}
