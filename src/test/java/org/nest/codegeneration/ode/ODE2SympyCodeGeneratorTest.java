/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.ode;

import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.Names;
import org.junit.Test;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * TODO
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class ODE2SympyCodeGeneratorTest {
  private static final String TEST_MODEL_PATH = "src/test/resources/";

  public static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";

  private static final String OUTPUT_FOLDER = "target";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void generateSympyScript() throws IOException {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);

    assertTrue(root.isPresent());
    final String packageName = Names.getQualifiedName(root.get().getPackageName().getParts());

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final File outputFolder = new File(OUTPUT_FOLDER + File.separator + Names.getPathFromPackage(packageName));

    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.get().getNeurons().get(0).getBody());
    final Optional<ASTOdeDeclaration> odeDeclaration = astBodyDecorator.getOdeDefinition();

    assertTrue(odeDeclaration.isPresent());
    ODE2SympyCodeGenerator.generateSympyODEAnalyzer(glex, odeDeclaration.get(), outputFolder, "iaf_neuron");
  }

  private GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

}
