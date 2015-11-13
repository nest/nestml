/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest;

import de.se_rwth.commons.logging.Log;
import org.junit.BeforeClass;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.IOException;

import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Disables exit on error and provides base services for parsing and symbol table.
 *
 * @author plotnikov
 */
public class ModelTestBase {

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

}
