/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.frontend.CliConfiguration;
import org.nest.frontend.NestmlFrontend;
import org.nest.utils.FilesHelper;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Tests the entire pipeline.
 *
 * @author plotnikov
 */
public class NestmlFrontendIntegrationTest {
  private final NestmlFrontend nestmlFrontend = new NestmlFrontend();
  private static final Path outputPath = Paths.get("target", "integration");

  @Test
  public void testRunUserDefinedOutputFolder() {
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/command_line_base", "--target", outputPath.toString()});
  }

  @Test
  public void testInheritance() {
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/inheritance", "--target", outputPath.toString()});
  }

  @Ignore("PIP supports only 1.0.0 sympy")
  @Test
  public void testInfrastructure() {
    FilesHelper.deleteFilesInFolder(outputPath);
    final CliConfiguration cliConfiguration = nestmlFrontend.createCLIConfiguration(new String[] {
        "models",
        "--target", outputPath.toString()});
    Assert.assertTrue(NestmlFrontend.checkEnvironment(cliConfiguration));
  }

  @Test
  public void testModelsFolder() {
    final String[] args = new String[] {
        "models",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

  @Test
  public void testTutorialModels() {
    final String[] args = new String[] {
        "src/test/resources/tutorial",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

  @Test
  public void manually() {
    final String[] args = new String[] {
        "models/ht_neuron.nestml",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

  @Test
  public void debug() {
    final String[] args = new String[] {
        "debug",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

  @Test
  public void testShowcase() {
    final String[] args = new String[] {
        "showcase",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

}
