/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import org.junit.Assert;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.codegeneration.NestCodeGenerator;
import org.nest.mocks.PSCMock;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;

/**
 * Mocks the codegenerator and tests executor functions.
 *
 * @author plotnikov
 */
public class CliConfigurationExecutorTest extends ModelbasedTest {
  private static final Path TEST_INPUT_PATH = Paths.get("src/test/resources/command_line_base/");
  private static final Path TARGET_FOLDER = Paths.get("target/build");
  private final PSCMock pscMock = new PSCMock();
  private final CliConfiguration testConfig;
  private final CliConfigurationExecutor executor = new CliConfigurationExecutor();
  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_INPUT_PATH);

  public CliConfigurationExecutorTest() {
    testConfig = new CliConfiguration.Builder()
        .withCoCos()
        .withInputBasePath(TEST_INPUT_PATH)
        .withTargetPath(TARGET_FOLDER)
        .build();
  }

  @Test
  public void testExecutionTestConfiguration() {
    final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator, pscMock, true);
    executor.execute(generator, testConfig);
  }

  @Test
  public void testArtifactCollection() {
    final List<Path> collectedFiles = collectNESTMLModelFilenames(TEST_INPUT_PATH);
    Assert.assertEquals(2, collectedFiles.size());
  }

}
