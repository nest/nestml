package org.nest.codegeneration.sympy;

import org.junit.Ignore;
import org.junit.Test;
import org.nest.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.io.File;
import java.nio.file.Paths;

import static de.se_rwth.commons.Names.getPathFromPackage;
import static de.se_rwth.commons.Names.getQualifiedName;

/**
 * Tests if the overall transformation process works
 *
 * @author plotnikov
 */
public class ODEProcessorTest extends ModelTestBase {

  private static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";
  final ODEProcessor testant = new ODEProcessor();

  @Ignore
  @Test
  public void testProcess() throws Exception {
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    String modelFolder = getPathFromPackage(
        getQualifiedName(modelRoot.getPackageName().getParts()));
    testant.process(modelRoot, new File(Paths.get("target", modelFolder).toString()));
  }

}