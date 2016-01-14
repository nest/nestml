/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.symboltable;

import de.monticore.symboltable.Scope;
import org.junit.Test;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTBodyElement;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.UsageSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

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
  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
  private final Scope globalScope = scopeCreator.getGlobalScope();

  @Test
  public void testCreationOfSymtabAndResolvingOfSymbols() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    Collection<TypeSymbol> nestmlTypes = modelScope.resolveLocally(NeuronSymbol.KIND);
    assertEquals(2, nestmlTypes.size());

    final Optional<TypeSymbol> neuronTypeOptional = modelScope.resolve(
        "iaf_neuron",
        NeuronSymbol.KIND);
    assertTrue(neuronTypeOptional.isPresent());

    final Optional<TypeSymbol> testComponentOptional = modelScope.resolve(
        "TestComponent",
        NeuronSymbol.KIND);
    assertTrue(testComponentOptional.isPresent());

    final Optional<TypeSymbol> testComponentFromGlobalScope = globalScope.resolve(
        "org.nest.nestml.symboltable.iaf_neuron.TestComponent", NeuronSymbol.KIND);
    assertTrue(testComponentFromGlobalScope.isPresent());
  }

  @Test
  public void testResolvingFromSeparateBlocks() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

    final Optional<ASTBodyElement> neuronState = astBodyDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());

    // retrieve state block
    final Scope stateScope = neuronState.get().getEnclosingScope().get();
    Optional<VariableSymbol> y0Symbol = stateScope.resolve("y0", VariableSymbol.KIND);
    assertTrue(y0Symbol.isPresent());

    // retrieve parameter block
    final Scope parameterScope = astBodyDecorator.getParameterBlock().get().getEnclosingScope().get();
    assertSame(stateScope, parameterScope);
    assertTrue(parameterScope.resolve("y0", VariableSymbol.KIND).isPresent());
    assertTrue(parameterScope.resolve("C_m", VariableSymbol.KIND).isPresent());

    // retrieve dynamics block
    final Scope dynamicsScope = astBodyDecorator.getDynamics().get(0).getBlock().getEnclosingScope().get();

    final Optional<VariableSymbol> newVarInMethodSymbol
        = dynamicsScope.resolve("newVarInMethod", VariableSymbol.KIND);
    assertTrue(newVarInMethodSymbol.isPresent());
    assertTrue(newVarInMethodSymbol.get().getType().equals(PredefinedTypes.getRealType()));


  }

  @Test
  public void testShadowingOfVariablesInMethods() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());

    final Optional<ASTBodyElement> neuronState = astBodyDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());
    final Optional<VariableSymbol> testVarFromParameter =
        neuronState.get().getEnclosingScope().get().resolve("scopeTestVar",
            VariableSymbol.KIND);

    // check the symbol from parameter block
    assertTrue(testVarFromParameter.isPresent());
    assertTrue(testVarFromParameter.get().getType().equals(PredefinedTypes.getStringType()));

    // check the symbol in function block
    final Optional<ASTFunction> scopeTestingFunction = astBodyDecorator
        .getFunctions()
        .stream()
        .filter(astFunction -> astFunction.getName().equals("scopeTestingFunction"))
        .findFirst();

    assertTrue(scopeTestingFunction.isPresent());
    final Optional<VariableSymbol> testVarFromFunction =
        scopeTestingFunction.get().getBlock().getEnclosingScope().get().resolve("scopeTestVar", VariableSymbol.KIND);
    assertTrue(testVarFromFunction.isPresent());
    assertTrue(testVarFromFunction.get().getType().equals(PredefinedTypes.getIntegerType()));

    // retrieve the if block and resolve it from there
    final Optional<VariableSymbol> testVarFromIfBlock =
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
            .resolve("scopeTestVar", VariableSymbol.KIND);

    assertTrue(testVarFromIfBlock.isPresent());
    assertTrue(testVarFromIfBlock.get().getType().equals(PredefinedTypes.getRealType()));
  }

  @Test
  public void testPredefinedVariables() throws IOException {
    final ASTNESTMLCompilationUnit root = getNestmlRootFromFilename(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    final Optional<VariableSymbol> fromGlobalScope
        = globalScope.resolve("e", VariableSymbol.KIND);
    assertTrue(fromGlobalScope.isPresent());


    final Optional<VariableSymbol> fromModelScope
        = modelScope.resolve("e", VariableSymbol.KIND);
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
    final Optional<NeuronSymbol> usingNeuronSymbol = modelScope
        .resolve("org.nest.nestml.symboltable.importingNeuron.UsingNeuron", NeuronSymbol.KIND);
    assertTrue(usingNeuronSymbol.isPresent());
    final Scope neuronScope = usingNeuronSymbol.get().getSpannedScope();

    final Optional<UsageSymbol> usageSymbol = neuronScope
        .resolve("TestReference", UsageSymbol.KIND);
    assertTrue(usageSymbol.isPresent());

    final NeuronSymbol componentSymbol = usageSymbol.get().getReferencedSymbol();
    assertEquals(NeuronSymbol.Type.COMPONENT, componentSymbol.getType());
  }

}
