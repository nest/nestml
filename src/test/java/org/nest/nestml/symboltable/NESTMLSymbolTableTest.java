/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.symboltable;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.*;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.MethodSignaturePredicate;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.spl._ast.ASTAssignment;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.*;
import org.nest.utils.ASTNodes;
import org.nest.utils.NESTMLSymbols;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.nest.utils.NESTMLSymbols.resolveMethod;

/**
 *  Tests the symbol table infrastructure of the NESTML language
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableTest extends ModelbasedTest {

  private static final String MODEL_FILE_NAME = "src/test/resources/org/nest/nestml/symboltable/"
      + "iaf_neuron.nestml";
  private static final String USING_NEURON_FILE = "src/test/resources/org/nest/nestml/symboltable/"
      + "importingNeuron.nestml";

  private static final String MODEL_WITH_INHERITANCE =
      "src/test/resources/inheritance/iaf_neuron.nestml";

  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);

  @Test
  public void testCreationOfSymtabAndResolvingOfSymbols() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
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

    final Optional<TypeSymbol> testComponentFromGlobalScope = scopeCreator.getGlobalScope().resolve(
        "org.nest.nestml.symboltable.iaf_neuron.TestComponent", NeuronSymbol.KIND);
    assertTrue(testComponentFromGlobalScope.isPresent());
  }

  @Test
  public void testResolvingFromSeparateBlocks() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTBody astBodyDecorator = (root.getNeurons().get(0).getBody());

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
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTBody astBodyDecorator = (root.getNeurons().get(0).getBody());

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
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    final Optional<VariableSymbol> fromGlobalScope
        = scopeCreator.getGlobalScope().resolve("e", VariableSymbol.KIND);
    assertTrue(fromGlobalScope.isPresent());


    final Optional<VariableSymbol> fromModelScope
        = modelScope.resolve("e", VariableSymbol.KIND);
    assertTrue(fromModelScope.isPresent());
  }

  @Test
  public void testPredefinedMethods() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    final Optional<MethodSymbol> fromGlobalScope
        = scopeCreator.getGlobalScope().resolve("exp", MethodSymbol.KIND);
    assertTrue(fromGlobalScope.isPresent());


    final Optional<MethodSymbol> fromModelScope = modelScope.resolve("exp", MethodSymbol.KIND);
    assertTrue(fromModelScope.isPresent());

    final Optional<MethodSymbol> withPredicate
        = NESTMLSymbols.resolveMethod("exp", Lists.newArrayList("real"), modelScope);
    assertTrue(withPredicate.isPresent());
  }

  @Test
  public void testResolvingSeparateModels() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(USING_NEURON_FILE);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);
    final Optional<NeuronSymbol> usingNeuronSymbol = modelScope
        .resolve("org.nest.nestml.symboltable.importingNeuron.UsingNeuron", NeuronSymbol.KIND);
    assertTrue(usingNeuronSymbol.isPresent());
    final Scope neuronScope = usingNeuronSymbol.get().getSpannedScope();

    final Optional<UsageSymbol> usageSymbol = neuronScope.resolve("TestReference", UsageSymbol.KIND);
    assertTrue(usageSymbol.isPresent());
    assertNotNull(usageSymbol.get().getReferencedSymbol().getName());

    final NeuronSymbol componentSymbol = usageSymbol.get().getReferencedSymbol();
    assertEquals(NeuronSymbol.Type.COMPONENT, componentSymbol.getType());
  }

  @Test
  public void testResolvingOfPredefinedFunctions() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTBody astBodyDecorator = (root.getNeurons().get(0).getBody());

    final Optional<ASTBodyElement> neuronState = astBodyDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());

    // retrieve state block
    final Scope stateScope = neuronState.get().getEnclosingScope().get();
    Optional<VariableSymbol> y0Symbol = stateScope.resolve("y0", VariableSymbol.KIND);
    assertTrue(y0Symbol.isPresent());

    List<String> parameters = Lists.newArrayList("mV");

    final Optional<MethodSymbol> standAloneFunction = (Optional<MethodSymbol>)
        stateScope.resolve(new MethodSignaturePredicate(PredefinedFunctions.INTEGRATE, parameters));
    standAloneFunction.isPresent();
  }

  @Test
  public void testResolvingPredefinedFunctions() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());
    scopeCreator.runSymbolTableCreator(root);
    final ScopeSpanningSymbol symbol = (ScopeSpanningSymbol) root.getNeurons().get(0).getSymbol().get();
    final Scope scope = symbol.getSpannedScope();//scopeCreator.runSymbolTableCreator(root);

    scope.resolve(PredefinedFunctions.I_SUM, MethodSymbol.KIND);
    final Optional<MethodSymbol> method1 = resolveMethod(
        PredefinedFunctions.I_SUM, Lists.newArrayList("real", "Buffer"), scope
    );

    assertTrue(method1.isPresent());

    final Optional<MethodSymbol> method2 = resolveMethod(
        PredefinedFunctions.INTEGRATE, Lists.newArrayList("boolean"), scope
    );
    assertFalse(method2.isPresent());

    final Optional<MethodSymbol> method3 = resolveMethod(
        PredefinedFunctions.INTEGRATE, Lists.newArrayList("real"), scope
    );
    assertTrue(method3.isPresent());
  }

  @Test
  public void testResolvingFromSupertype() throws IOException {
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(Paths.get("src/test/resources/inheritance"));
    final NESTMLParser nestmlParser = new NESTMLParser(Paths.get("src/test/resources/inheritance"));
    final ASTNESTMLCompilationUnit root = nestmlParser.parse(MODEL_WITH_INHERITANCE.toString()).get();
    assertEquals(1, root.getNeurons().size());
    scopeCreator.runSymbolTableCreator(root);
    ASTNeuron astNeuron = root.getNeurons().get(0);
    assertTrue( astNeuron.getSymbol().isPresent());
    assertTrue( astNeuron.getSymbol().get() instanceof NeuronSymbol);
    final NeuronSymbol neuronSymbol = (NeuronSymbol) astNeuron.getSymbol().get();
    /*Optional<VariableSymbol> internalVariable = neuronSymbol.getSpannedScope().resolve("tau_m", VariableSymbol.KIND);
    assertTrue(internalVariable.isPresent());

    Optional<VariableSymbol> importedVariable = neuronSymbol.getSpannedScope().resolve("r", VariableSymbol.KIND);
    assertTrue(importedVariable.isPresent());
*/
    final Optional<ASTAssignment> astAssignment = ASTNodes.getAny(root, ASTAssignment.class);
    assertTrue(astAssignment.isPresent());
    final Optional<VariableSymbol> fromAssignment = astAssignment.get().getEnclosingScope().get()
        .resolve("r", VariableSymbol.KIND);

    assertTrue(fromAssignment.isPresent());
  }

}
