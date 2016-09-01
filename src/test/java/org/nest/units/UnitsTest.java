/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Before;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLCoCosManager;

import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.NESTMLRootCreator.getAstRoot;

/**
 * Checks that the SI unit checking works stable.
 *
 * @author traeder, plotnikov
 */
public class UnitsTest extends ModelbasedTest {

  @Before
  public void clearLog() {
    Log.enableFailQuick(false);
    Log.getFindings().clear();
  }

  @Test
  public void test_unit_errors_produce_warnings() {
    final NESTMLCoCosManager completeChecker = new NESTMLCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "src/test/resources/org/nest/units/validExpressions.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());

    List<Finding> findings = completeChecker.analyzeModel(validRoot.get());
    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();

    assertEquals(0, errorsFound);
    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        "src/test/resources/org/nest/units/invalidExpressions.nestml", TEST_MODEL_PATH);

    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());
    findings = completeChecker.analyzeModel(invalidRoot.get());

    errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING))
        .count();

    assertEquals(17, errorsFound);
  }

  @Test
  public void test_iaf_cond_alpha() {
    final NESTMLCoCosManager completeChecker = new NESTMLCoCosManager();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "models/iaf_cond_alpha.nestml", TEST_MODEL_PATH);
    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    final List<Finding> findings = completeChecker.analyzeModel(validRoot.get());

    long errorsFound = findings
        .stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
        .count();
    assertEquals(0, errorsFound);
  }

}
