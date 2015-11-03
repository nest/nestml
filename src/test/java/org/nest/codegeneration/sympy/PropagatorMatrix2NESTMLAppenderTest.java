/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.DisableFailQuickMixin;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.sympy.PropagatorMatrix2NESTMLAppender;
import org.nest.sympy.SymPyOutput2NESTMLConverter;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class PropagatorMatrix2NESTMLAppenderTest extends DisableFailQuickMixin {
  private final static String GENERATED_MATRIX_PATH = "src/test/resources/sympy/solution.matrix.tmp";

  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void testResolvingProblem() throws Exception {
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(MODEL_FILE_PATH);
    assertTrue(root.isPresent());

    final SymPyOutput2NESTMLConverter symPyOutput2NESTMLConverter = new SymPyOutput2NESTMLConverter();
    final List<ASTAliasDecl> testant = symPyOutput2NESTMLConverter.createDeclarationASTs(GENERATED_MATRIX_PATH);
    assertEquals(9, testant.size());
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.get()
        .getNeurons()
        .get(0)
        .getBody());

    testant.forEach(astBodyDecorator::addToInternalBlock);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    System.out.println("Printed model:\n" + prettyPrint(root));

    // todo
    Optional<NESTMLVariableSymbol> p30 = astBodyDecorator
        .getInternals().get(0)
        .getEnclosingScope().get()
        .resolve("P30", NESTMLVariableSymbol.KIND);
    //assertTrue(p30.isPresent());

    Optional<NESTMLVariableSymbol> p01 = astBodyDecorator
        .getInternals().get(0)
        .getEnclosingScope().get()
        .resolve("P01", NESTMLVariableSymbol.KIND);
    assertTrue(p01.isPresent());
  }

  @Test
  public void testAddingPropagatorMatrix() {
    final PropagatorMatrix2NESTMLAppender propagatorMatrix2NESTMLAppender = new PropagatorMatrix2NESTMLAppender();
    // false abstraction level
    propagatorMatrix2NESTMLAppender.addPropagatorMatrixAndPrint(
        parseModel(MODEL_FILE_PATH),
        GENERATED_MATRIX_PATH,
        "target/tmp.nestml");
  }

  private String prettyPrint(final Optional<ASTNESTMLCompilationUnit> root) {
    final NESTMLPrettyPrinter nestmlPrettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.get().accept(nestmlPrettyPrinter);
    return nestmlPrettyPrinter.getResult();
  }

  private ASTNESTMLCompilationUnit parseModel(String pathToModel)  {
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();

    try {
      return p.parse(pathToModel).get();
    }
    catch (final IOException e) {
      throw new RuntimeException("Cannot parse the NESTML model: " + pathToModel, e);
    }

  }

}
