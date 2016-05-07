/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.frontend.CLIConfiguration;
import org.nest.frontend.NESTMLFrontend;
import org.nest.utils.FilesHelper;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Tests the entire pipeline.
 *
 * @author plotnikov
 */
@Ignore("Don't run this tests on github. PIP uses to outdated sympy package.")
public class NESTMLFrontendIntegrationTest {
  private final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();

  @Test
  public void testRunUserDefinedOutputFolder() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/command_line_base", "--target", outputPath.toString()});
  }

  @Test
  public void testInheritance() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/inheritance", "--target", outputPath.toString()});
  }

  @Test
  public void testBluegeneModels() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/codegeneration/bluegene", "--target", outputPath.toString()});
  }

  @Test
  public void testModelsWithInheritance() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/inheritance",  "--target", outputPath.toString()});
  }

  @Test
  public void testIzhikevichModel() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/codegeneration/izhikevich", "--target", outputPath.toString()});
  }


  @Test
  public void testGIFModel() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/codegeneration/gif", "--target", outputPath.toString()});
  }

  @Test
  public void testInfrastructure() {
    Path outputPath = Paths.get("target", "tmpOutput");
    FilesHelper.deleteFilesInFolder(outputPath);
    final CLIConfiguration cliConfiguration = nestmlFrontend.createCLIConfiguration(new String[] {
        "src/test/resources/codegeneration/gif",
        "--target", outputPath.toString()});
    Assert.assertTrue(NESTMLFrontend.checkEnvironment(cliConfiguration));
  }

}
