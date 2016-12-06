/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.ScopeSpanningSymbol;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.*;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.spl._ast.ASTAssignment;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.*;
import org.nest.utils.AstUtils;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.nest.symboltable.NESTMLSymbols.resolveMethod;

/**
 *  Tests the symbol table infrastructure of the NESTML language
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableCreatorTest extends ModelbasedTest {

  private static final String MODEL_FILE_NAME = "src/test/resources/org/nest/nestml/_symboltable/"
      + "iaf_neuron.nestml";
  private static final String USING_NEURON_FILE = "src/test/resources/org/nest/nestml/_symboltable/"
      + "importingNeuron.nestml";

  private static final String MODEL_WITH_INHERITANCE =
      "src/test/resources/inheritance/iaf_neuron.nestml";

  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(Paths.get("src/test/resources"));

  @Test
  public void testCreationOfSymtabAndResolvingOfSymbols() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    Collection<TypeSymbol> nestmlTypes = modelScope.resolveLocally(NeuronSymbol.KIND);
    assertEquals(2, nestmlTypes.size());

    final Optional<NeuronSymbol> neuronTypeOptional = modelScope.resolve(
        "iaf_neuron",
        NeuronSymbol.KIND);
    assertTrue(neuronTypeOptional.isPresent());
    final Optional<VariableSymbol> y0TVariable = neuronTypeOptional.get().getSpannedScope().resolve("y0", VariableSymbol.KIND);
    final Optional<VariableSymbol> y1Varialbe = neuronTypeOptional.get().getSpannedScope().resolve("y1", VariableSymbol.KIND);
    assertTrue(y0TVariable.isPresent());
    assertTrue(y0TVariable.get().definedByODE());
    assertTrue(y0TVariable.get().isLoggable());

    assertTrue(y1Varialbe.isPresent());
    assertFalse(y1Varialbe.get().definedByODE());
    assertTrue(y1Varialbe.get().isLoggable());

    // Checks that the derived variable is also resolvable
    final Optional<VariableSymbol> Dy0Varialbe = neuronTypeOptional.get().getSpannedScope().resolve("y0'", VariableSymbol.KIND);
    assertTrue(Dy0Varialbe.isPresent());
    assertTrue(Dy0Varialbe.get().definedByODE());

    final Optional<NeuronSymbol> testComponentOptional = modelScope.resolve(
        "TestComponent",
        NeuronSymbol.KIND);
    assertTrue(testComponentOptional.isPresent());

    final Optional<TypeSymbol> testComponentFromGlobalScope = scopeCreator.getGlobalScope().resolve(
        "org.nest.nestml._symboltable.iaf_neuron.TestComponent", NeuronSymbol.KIND);
    assertTrue(testComponentFromGlobalScope.isPresent());

    final Optional<VariableSymbol> C_mVarialbe = neuronTypeOptional.get().getSpannedScope().resolve("C_m", VariableSymbol.KIND);
    assertTrue(C_mVarialbe.isPresent());
    assertTrue(C_mVarialbe.get().isLoggable());

    final Optional<VariableSymbol> y3_tmpVarialbe = neuronTypeOptional.get().getSpannedScope().resolve("y3_tmp", VariableSymbol.KIND);
    assertTrue(y3_tmpVarialbe.isPresent());
    assertTrue(y3_tmpVarialbe.get().isLoggable());
  }

  /**
   * Tests the resolving of the variables which are 'shadowed' in inner blocks
   */
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
            .getSmall_Stmt().get()
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
        = resolveMethod("exp", Lists.newArrayList("real"), modelScope);
    assertTrue(withPredicate.isPresent());

    Optional<MethodSymbol> I_sumOptional = resolveMethod(PredefinedFunctions.CURR_SUM, Lists.newArrayList("pA", "Buffer"), modelScope);
    assertTrue(I_sumOptional.isPresent());
    I_sumOptional = resolveMethod(PredefinedFunctions.CURR_SUM, Lists.newArrayList("nS", "Buffer"), modelScope);
    assertFalse(I_sumOptional.isPresent());
    I_sumOptional = resolveMethod(PredefinedFunctions.CURR_SUM, Lists.newArrayList("pA", "real"), modelScope);
    assertFalse(I_sumOptional.isPresent());

    Optional<MethodSymbol> Cond_sumOptional = resolveMethod(PredefinedFunctions.COND_SUM, Lists.newArrayList("nS", "Buffer"), modelScope);
    assertTrue(Cond_sumOptional.isPresent());
    Cond_sumOptional = resolveMethod(PredefinedFunctions.COND_SUM, Lists.newArrayList("pA", "Buffer"), modelScope);
    assertFalse(Cond_sumOptional.isPresent());
    Cond_sumOptional = resolveMethod(PredefinedFunctions.COND_SUM, Lists.newArrayList("nS", "real"), modelScope);
    assertFalse(Cond_sumOptional.isPresent());
  }

  @Test
  public void testResolvingSeparateModels() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(USING_NEURON_FILE);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);
    final Optional<NeuronSymbol> usingNeuronSymbol = modelScope
        .resolve("org.nest.nestml._symboltable.importingNeuron.UsingNeuron", NeuronSymbol.KIND);
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

    final Optional<MethodSymbol> standAloneFunction = resolveMethod(PredefinedFunctions.INTEGRATE_ODES, parameters, stateScope);
    standAloneFunction.isPresent();
  }

  @Test
  public void testResolvingPredefinedFunctions() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());
    scopeCreator.runSymbolTableCreator(root);
    final ScopeSpanningSymbol symbol = (ScopeSpanningSymbol) root.getNeurons().get(0).getSymbol().get();
    final Scope scope = symbol.getSpannedScope();

    final Optional<MethodSymbol> method2 = resolveMethod(
        PredefinedFunctions.INTEGRATE_ODES, Lists.newArrayList("boolean"), scope
    );
    assertFalse(method2.isPresent());

    final Optional<MethodSymbol> method3 = resolveMethod(
        PredefinedFunctions.INTEGRATE_ODES,
        Lists.newArrayList(),
        scope);
    assertTrue(method3.isPresent());
  }

  @Test
  public void testResolvingFromSupertype() throws IOException {
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(Paths.get("src/test/resources/inheritance"));
    final NESTMLParser nestmlParser = new NESTMLParser(Paths.get("src/test/resources/inheritance"));
    final ASTNESTMLCompilationUnit root = nestmlParser.parse(MODEL_WITH_INHERITANCE).get();
    assertEquals(1, root.getNeurons().size());
    scopeCreator.runSymbolTableCreator(root);
    ASTNeuron astNeuron = root.getNeurons().get(0);
    assertTrue( astNeuron.getSymbol().isPresent());
    assertTrue( astNeuron.getSymbol().get() instanceof NeuronSymbol);
    final NeuronSymbol neuronSymbol = (NeuronSymbol) astNeuron.getSymbol().get();
    Optional<VariableSymbol> internalVariable = neuronSymbol.getSpannedScope().resolve("tau_m", VariableSymbol.KIND);
    assertTrue(internalVariable.isPresent());

    Optional<VariableSymbol> importedVariable = neuronSymbol.getSpannedScope().resolve("r", VariableSymbol.KIND);
    assertTrue(importedVariable.isPresent());

    final Optional<ASTAssignment> astAssignment = AstUtils.getAny(root, ASTAssignment.class);
    assertTrue(astAssignment.isPresent());
    final Optional<VariableSymbol> fromAssignment = astAssignment.get().getEnclosingScope().get()
        .resolve("r", VariableSymbol.KIND);

    assertTrue(fromAssignment.isPresent());
  }

  @Test
  public void testRecognitionOfConductanceBasedBuffers() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());
    scopeCreator.runSymbolTableCreator(root);

    final List<VariableSymbol> spikeBuffers = root.getNeurons().get(0).getBody().getSpikeBuffers();
    assertTrue(spikeBuffers.size() == 1);
    assertTrue(spikeBuffers.get(0).isConductanceBased());
  }
}
