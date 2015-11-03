/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.sympy;

import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Tests how the pyhton output is processed in the NESTML tooling.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class ModelConverterTest {
  private final static String GENERATED_MATRIX_PATH = "src/test/resources/org/nest/sympy/solution.matrix.tmp";

  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @BeforeClass
  public static void initLog() {
    Log.enableFailQuick(false);

  }

  @Test
  public void testResolvingProblem() throws Exception {
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);
    assertTrue(root.isPresent());

    final Sympy2NESTMLConverter sympy2NESTMLConverter = new Sympy2NESTMLConverter();
    final List<ASTAliasDecl> testant = sympy2NESTMLConverter.convertMatrixFile2NESTML(GENERATED_MATRIX_PATH);
    assertEquals(9, testant.size());
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.get().getNeurons().get(0).getBody());

    testant.forEach(astBodyDecorator::addToInternalBlock);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    printTransformedModel(root);

    Optional<NESTMLVariableSymbol> p30 = astBodyDecorator
        .getInternals().get(0)
        .getEnclosingScope().get()
        .resolve("P30", NESTMLVariableSymbol.KIND);
    //assertTrue(p30.isPresent()); todo

    Optional<NESTMLVariableSymbol> p01 = astBodyDecorator
        .getInternals().get(0)
        .getEnclosingScope().get()
        .resolve("P01", NESTMLVariableSymbol.KIND);
    assertTrue(p01.isPresent());
  }

  private void printTransformedModel(final Optional<ASTNESTMLCompilationUnit> root) {
    final NESTMLPrettyPrinter nestmlPrettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.get().accept(nestmlPrettyPrinter);
    System.out.println(nestmlPrettyPrinter.getResult());
  }

  @Test
  public void testAddingPropagatorMatrix() {
    final ModelConverter modelConverter = new ModelConverter();
    modelConverter.addPropagatorMatrixAndPrint(MODEL_FILE_PATH, GENERATED_MATRIX_PATH, "target/tmp.nestml");
  }


}
