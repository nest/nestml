package org.nest.units;

import static de.se_rwth.commons.logging.Log.getErrorCount;
import static de.se_rwth.commons.logging.Log.getFindings;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.NESTMLRootCreator.getAstRoot;
import static org.nest.utils.LogHelper.countWarningsByPrefix;

import java.util.Optional;

import de.se_rwth.commons.logging.Log;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.AliasHasNoSetter;
import org.nest.nestml._cocos.LiteralsHaveTypes;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.units._visitor.UnitsSIVisitor;

/**
 * @author ptraeder
 */
public class UnitsTest extends ModelbasedTest {

  @Before
  public void clearLog() {
    Log.enableFailQuick(false);
    Log.getFindings().clear();
  }

  @After
  public void printErrorMessage() {
    getFindings().forEach(e -> System.out.println("Error found: " + e));
  }

  @Test
  public void testUnit() {
    final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();
    final NESTMLCoCoChecker completeChecker= nestmlCoCosManager.createNESTMLCheckerWithSPLCocos();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "src/test/resources/org/nest/units/validExpressions.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    completeChecker.checkAll(validRoot.get());

    long findings = getFindings().size();
    assertEquals(0, findings);
    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        "src/test/resources/org/nest/units/invalidExpressions.nestml", TEST_MODEL_PATH);

    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());
    completeChecker.checkAll(invalidRoot.get());

    findings = getFindings().size();
    assertEquals(8, findings);
  }
  @Test
  public void test_iaf_cond_alpha() {
    final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();
    final NESTMLCoCoChecker completeChecker= nestmlCoCosManager.createNESTMLCheckerWithSPLCocos();
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        "models/iaf_cond_alpha.nestml", TEST_MODEL_PATH);

    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    completeChecker.checkAll(validRoot.get());

    long errorsFound = getErrorCount();
    assertEquals(0, errorsFound);
  }

}
