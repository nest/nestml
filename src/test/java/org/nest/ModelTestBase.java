/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest;

import de.se_rwth.commons.logging.Log;
import org.apache.commons.io.FileUtils;
import org.junit.BeforeClass;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.io.IOException;

import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Disables exit on error and provides base services for parsing and symbol table.
 *
 * @author plotnikov
 */
public class ModelTestBase {

  protected static final String OUTPUT_FOLDER = "target";

  protected static final String TEST_MODEL_PATH = "src/test/resources/";

  protected static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH, typesFactory);

  @BeforeClass
  public static void disableFailQuick() {
    Log.enableFailQuick(false);
  }

  public ASTNESTMLCompilationUnit parseNESTMLModel(final String pathToModel)  {
    final NESTMLCompilationUnitMCParser p = createNESTMLCompilationUnitMCParser();

    try {
      return p.parse(pathToModel).get();
    }
    catch (final IOException e) {
      throw new RuntimeException("Cannot parse the NESTML model: " + pathToModel, e);
    }

  }

  protected void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputModelFile) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputModelFile);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputModelFile, e);
    }
  }
}
