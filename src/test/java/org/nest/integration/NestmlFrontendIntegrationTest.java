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
import java.util.Optional;

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
    nestmlFrontend.start(new String[] {"src/test/resources/inheritance", "-t", outputPath.toString()});
  }

  @Ignore("PIP supports only 1.0.0 sympy")
  @Test
  public void testInfrastructure() {
    FilesHelper.deleteFilesInFolder(outputPath);
    final Optional<CliConfiguration> cliConfiguration = nestmlFrontend.createCLIConfiguration(new String[] {
        "models",
        "--json_log", "model_issues",
        "--target", outputPath.toString()});
    Assert.assertTrue(cliConfiguration.isPresent());
    Assert.assertTrue(NestmlFrontend.checkEnvironment(cliConfiguration.get()));
  }

  @Test
  public void testDryRun() {
    final String[] args = new String[] {
        "models/",
        "--target", outputPath.toString(),
        "--dry-run"};

    new NestmlFrontend().start(args);
  }

  @Test
  public void testJsonOutput() {
    final String[] args = new String[] {
        "models/",
        "--target", outputPath.toString(),
        "--target", outputPath.toString(),
        "--dry-run"};

    new NestmlFrontend().start(args);
  }

  @Test
  public void testModelsFolder() {
    final String[] args = new String[] {
        "models/",
        "--json_log", "model_issues",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

  @Test
  public void testTutorialModels() {
    final String[] args = new String[] {
        "src/test/resources/tutorial",
        "--json_log", "model_issues",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }

  @Test
  public void manually() {
    final String[] args = new String[] {
        "models/hh_cond_exp_traub.nestml",
        "--json_log", "model_issues",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }


}
