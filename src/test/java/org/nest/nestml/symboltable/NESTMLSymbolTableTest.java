/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.symboltable;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import org.junit.Test;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTBodyElement;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.symboltable.symbols.NESTMLUsageSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.IOException;
import java.util.Collection;
import java.util.Optional;

import static org.junit.Assert.*;

/**
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLSymbolTableTest {

  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final String MODEL_FILE_NAME = "src/test/resources/org/nest/nestml/symboltable/"
      + "iaf_neuron.nestml";
  private static final String USING_NEURON_FILE = "src/test/resources/org/nest/nestml/symboltable/"
      + "importingNeuron.nestml";
  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();
  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH, typesFactory);
  private final Scope globalScope = scopeCreator.getGlobalScope();

  @Test
  public void testCreationOfSymtabAndResolvingOfSymbols() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    Collection<NESTMLTypeSymbol> nestmlTypes = modelScope.resolveLocally(NESTMLNeuronSymbol.KIND);
    assertEquals(2, nestmlTypes.size());

    final Optional<NESTMLTypeSymbol> neuronTypeOptional = modelScope.resolve(
        "iaf_neuron",
        NESTMLNeuronSymbol.KIND);
    assertTrue(neuronTypeOptional.isPresent());

    final Optional<NESTMLTypeSymbol> testComponentOptional = modelScope.resolve(
        "TestComponent",
        NESTMLNeuronSymbol.KIND);
    assertTrue(testComponentOptional.isPresent());

    final Optional<NESTMLTypeSymbol> testComponentFromGlobalScope = globalScope.resolve(
        "org.nest.nestml.symboltable.iaf_neuron.TestComponent", NESTMLNeuronSymbol.KIND);
    assertTrue(testComponentFromGlobalScope.isPresent());
  }

  @Test
  public void testResolvingFromSeparateBlocks() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final PredefinedTypesFactory predefinedTypesFactory = scopeCreator.getTypesFactory();
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

    final Optional<ASTBodyElement> neuronState = astBodyDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());

    // retrieve state block
    final Scope stateScope = neuronState.get().getEnclosingScope().get();
    Optional<NESTMLVariableSymbol> y0Symbol = stateScope.resolve("y0", NESTMLVariableSymbol.KIND);
    assertTrue(y0Symbol.isPresent());

    // retrieve parameter block
    final Scope parameterScope = astBodyDecorator.getParameterBlock().get().getEnclosingScope().get();
    assertSame(stateScope, parameterScope);
    assertTrue(parameterScope.resolve("y0", NESTMLVariableSymbol.KIND).isPresent());
    assertTrue(parameterScope.resolve("C_m", NESTMLVariableSymbol.KIND).isPresent());

    // retrieve dynamics block
    final Scope dynamicsScope = astBodyDecorator.getDynamics().get(0).getBlock().getEnclosingScope().get();

    final Optional<NESTMLVariableSymbol> newVarInMethodSymbol
        = dynamicsScope.resolve("newVarInMethod", NESTMLVariableSymbol.KIND);
    assertTrue(newVarInMethodSymbol.isPresent());
    assertTrue(newVarInMethodSymbol.get().getType().equals(predefinedTypesFactory.getRealType()));


  }

  @Test
  public void testShadowingOfVariablesInMethods() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final PredefinedTypesFactory predefinedTypesFactory = scopeCreator.getTypesFactory();
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

    final Optional<ASTBodyElement> neuronState = astBodyDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());
    final Optional<NESTMLVariableSymbol> testVarFromParameter =
        neuronState.get().getEnclosingScope().get().resolve("scopeTestVar",
            NESTMLVariableSymbol.KIND);

    // check the symbol from parameter block
    assertTrue(testVarFromParameter.isPresent());
    assertTrue(testVarFromParameter.get().getType().equals(predefinedTypesFactory.getStringType()));

    // check the symbol in function block
    final Optional<ASTFunction> scopeTestingFunction = astBodyDecorator
        .getFunctions()
        .stream()
        .filter(astFunction -> astFunction.getName().equals("scopeTestingFunction"))
        .findFirst();

    assertTrue(scopeTestingFunction.isPresent());
    final Optional<NESTMLVariableSymbol> testVarFromFunction =
        scopeTestingFunction.get().getBlock().getEnclosingScope().get().resolve("scopeTestVar", NESTMLVariableSymbol.KIND);
    assertTrue(testVarFromFunction.isPresent());
    assertTrue(testVarFromFunction.get().getType().equals(predefinedTypesFactory.getIntegerType()));

    // retrieve the if block and resolve it from there
    // TODO it should not be a correct solution
    final Optional<NESTMLVariableSymbol> testVarFromIfBlock =
        scopeTestingFunction.get()
            .getBlock()
            .getStmts().get(1) // retrieves the second statement from function
            .getCompound_Stmt().get()
            .getIF_Stmt().get()
            .getIF_Clause()
            .getBlock()
            .getStmts().get(0)
            .getSimple_Stmt().get()
            .getSmall_Stmts().get(0)
            .getDeclaration().get()
            .getEnclosingScope().get()
            .resolve("scopeTestVar", NESTMLVariableSymbol.KIND);

    assertTrue(testVarFromIfBlock.isPresent());
    assertTrue(testVarFromIfBlock.get().getType().equals(predefinedTypesFactory.getRealType()));
  }

  @Test
  public void testPredefinedVariables() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    final Optional<NESTMLVariableSymbol> fromGlobalScope
        = globalScope.resolve("E", NESTMLVariableSymbol.KIND);
    assertTrue(fromGlobalScope.isPresent());


    final Optional<NESTMLVariableSymbol> fromModelScope
        = modelScope.resolve("E", NESTMLVariableSymbol.KIND);
    assertTrue(fromModelScope.isPresent());
  }

  public ASTNESTMLCompilationUnit getNestmlRootFromFilename(final String modelFilename) throws IOException {
    final NESTMLParser p = new NESTMLParser();
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(modelFilename);
    assertTrue(root.isPresent());
    return root.get();
  }

  @Test
  public void testResolvingSeparateModels() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(USING_NEURON_FILE);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);
    final Optional<NESTMLNeuronSymbol> usingNeuronSymbol = modelScope
        .resolve("org.nest.nestml.symboltable.importingNeuron.UsingNeuron", NESTMLNeuronSymbol.KIND);
    assertTrue(usingNeuronSymbol.isPresent());
    final Scope neuronScope = usingNeuronSymbol.get().getSpannedScope();

    final Optional<NESTMLUsageSymbol> usageSymbol = neuronScope
        .resolve("TestReference", NESTMLUsageSymbol.KIND);
    assertTrue(usageSymbol.isPresent());

    final NESTMLNeuronSymbol componentSymbol = usageSymbol.get().getReferencedSymbol();
    assertEquals(NESTMLNeuronSymbol.Type.COMPONENT, componentSymbol.getType());
  }

}
