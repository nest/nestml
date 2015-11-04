/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import org.junit.Test;
import org.nest.DisableFailQuickMixin;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class ExactSolutionTransformerTest extends DisableFailQuickMixin {
  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH, new PredefinedTypesFactory());
  private final static String P00_FILE = "src/test/resources/codegeneration/sympy/P00.mat";
  private final static String PSC_INITIAL_VALUE_FILE = "src/test/resources/codegeneration/sympy/pscInitialValue.mat";
  private final static String STATE_VECTOR_FILE = "src/test/resources/codegeneration/sympy/state.vector.mat";
  private final static String UPDATE_STEP_FILE = "src/test/resources/codegeneration/sympy/update.step.mat";

  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void testAddingP00Value() {
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    // false abstraction level
    exactSolutionTransformer.addP00(
        parseModel(MODEL_FILE_PATH),
        P00_FILE,
        "target/tmp.nestml");
    ASTNESTMLCompilationUnit testant = parseModel("target/tmp.nestml");

    final Scope scope = scopeCreator.runSymbolTableCreator(testant);
    Optional<NESTMLNeuronSymbol> symbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> p00Symbol = symbol.get().getVariableByName("P00");

    assertTrue(p00Symbol.isPresent());
    assertTrue(p00Symbol.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.INTERNAL));
  }

  @Test
  public void testAddingPSCInitialValue() {
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    // false abstraction level
    exactSolutionTransformer.addPSCInitialValue(
        parseModel(MODEL_FILE_PATH),
        PSC_INITIAL_VALUE_FILE,
        "target/tmp.nestml");
    ASTNESTMLCompilationUnit testant = parseModel("target/tmp.nestml");

    final Scope scope = scopeCreator.runSymbolTableCreator(testant);

    Optional<NESTMLNeuronSymbol> symbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> pscInitialValue = symbol.get().getVariableByName("PSCInitialValue");

    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.INTERNAL));
  }

  private ASTNESTMLCompilationUnit parseModel(String pathToModel)  {
    final NESTMLCompilationUnitMCParser p = createNESTMLCompilationUnitMCParser();

    try {
      return p.parse(pathToModel).get();
    }
    catch (final IOException e) {
      throw new RuntimeException("Cannot parse the NESTML model: " + pathToModel, e);
    }

  }

}
