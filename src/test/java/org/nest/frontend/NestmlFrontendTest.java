/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import org.junit.Test;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.*;

/**
 * Tests various modis of the {@code NestmlFrontend} class. For this, several combinations of
 * CLI parameters also invalid combination are provided to the frontend.
 *
 * @author plotnikov
 */
public class NestmlFrontendTest {
  private final NestmlFrontend nestmlFrontend = new NestmlFrontend();

  @Test
  public void testCreationOfConfiguration() throws Exception {
    final Path testInputModelsPath = Paths.get("testInputModelsPath");
    final Path targetPath = Paths.get("testTargetPath");

    final Optional<CliConfiguration> testantLong = nestmlFrontend.createCLIConfiguration(new String[] {
        "--target", targetPath.toString(),
        "--enable_tracing",
        "--dry-run",
        "--json_log", Paths.get(targetPath.toString(), "model_log.log").toString(),
        "--module_name", "integration",
        testInputModelsPath.toString(),
    });

    assertTrue(testantLong.isPresent());
    assertTrue(testantLong.get().isTracing());
    assertFalse(testantLong.get().isCodegeneration());
    assertEquals(testInputModelsPath, testantLong.get().getInputPath());
    assertEquals(targetPath, testantLong.get().getTargetPath());
    assertEquals("integration", testantLong.get().getModuleName());

    final Optional<CliConfiguration> testantShort = nestmlFrontend.createCLIConfiguration(new String[] {
        "-t", targetPath.toString(),
        "-e",
        "-d",
        "-j", Paths.get(targetPath.toString(), "model_log.log").toString(),
        "-m", "integration",
        testInputModelsPath.toString(),
    });
    assertTrue(testantShort.isPresent());
    assertTrue(testantShort.get().isTracing());
    assertFalse(testantShort.get().isCodegeneration());
    assertEquals(testInputModelsPath, testantShort.get().getInputPath());
    assertEquals(targetPath, testantShort.get().getTargetPath());
    assertEquals("integration", testantShort.get().getModuleName());
  }

  @Test
  public void testUnparsableModels() {
    nestmlFrontend.start(new String[] {
        "src/test/resources/cli_unparsable",
        "--target", Paths.get("target", "cli_unparsable").toString()});
  }

  @Test
  public void testInvalidPath() {
    nestmlFrontend.start(new String[] {
        "--target", Paths.get("target", "cli_unparsable").toString(),
        "//bla/blu",});

    nestmlFrontend.start(new String[] {});
  }


  @Test
  public void testHelp() {
    nestmlFrontend.start(new String[] {});
  }

  private static final Path outputPath = Paths.get("target", "integration");

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
        "--enable_tracing",
        "--target", outputPath.toString()};

    new NestmlFrontend().start(args);
  }
}
