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
import org.nest.nestml._ast.ASTBlockWithVariables;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.io.IOException;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.nest.nestml._symboltable.NestmlSymbols.resolveMethod;

/**
 *  Tests the symbol table infrastructure of the NESTML language
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableCreatorTest extends ModelbasedTest {

  private static final String MODEL_FILE_NAME = "src/test/resources/org/nest/nestml/_symboltable/iaf_neuron.nestml";

  private final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator();

  @Test
  public void testCreationOfSymtabAndResolvingOfSymbols() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    Collection<TypeSymbol> nestmlTypes = modelScope.resolveLocally(NeuronSymbol.KIND);
    assertEquals(1, nestmlTypes.size());

    final Optional<NeuronSymbol> neuronTypeOptional = modelScope.resolve(
        "iaf_neuron",
        NeuronSymbol.KIND);
    assertTrue(neuronTypeOptional.isPresent());
    final Optional<VariableSymbol> y0TVariable = neuronTypeOptional.get().getSpannedScope().resolve("y0", VariableSymbol.KIND);
    final Optional<VariableSymbol> y1Varialbe = neuronTypeOptional.get().getSpannedScope().resolve("y1", VariableSymbol.KIND);
    assertTrue(y0TVariable.isPresent());
    assertTrue(y0TVariable.get().isInInitialValues());
    assertTrue(y0TVariable.get().getOdeDeclaration().isPresent());
    assertTrue(y0TVariable.get().isRecordable());

    assertTrue(y1Varialbe.isPresent());
    assertFalse(y1Varialbe.get().isInInitialValues());
    assertFalse(y1Varialbe.get().getOdeDeclaration().isPresent());

    // Checks that the derived variable is also resolvable
    final Optional<VariableSymbol> Dy0Varialbe = neuronTypeOptional.get().getSpannedScope().resolve("y0'", VariableSymbol.KIND);
    assertTrue(Dy0Varialbe.isPresent());
    assertTrue(Dy0Varialbe.get().isInInitialValues());
    assertTrue(Dy0Varialbe.get().getOdeDeclaration().isPresent());

    final Optional<VariableSymbol> C_mVarialbe = neuronTypeOptional.get().getSpannedScope().resolve("C_m", VariableSymbol.KIND);
    assertTrue(C_mVarialbe.isPresent());
    assertTrue(C_mVarialbe.get().isRecordable());

    final Optional<VariableSymbol> y3_tmpVarialbe = neuronTypeOptional.get().getSpannedScope().resolve("y3_tmp", VariableSymbol.KIND);
    assertTrue(y3_tmpVarialbe.isPresent());
    assertTrue(y3_tmpVarialbe.get().isRecordable());

    final Optional<VariableSymbol> r_Varialbe = neuronTypeOptional.get().getSpannedScope().resolve("r", VariableSymbol.KIND);
    assertTrue(r_Varialbe.isPresent());
  }

  /**
   * Tests the resolving of the variables which are 'shadowed' in inner blocks
   */
  @Test
  public void testResolvingFromSeparateBlocks() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTNeuron astNeuronDecorator = (root.getNeurons().get(0));

    final Optional<ASTBlockWithVariables> neuronState = astNeuronDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());

    // retrieve state block
    final Scope stateScope = neuronState.get().getEnclosingScope().get();
    Optional<VariableSymbol> y0Symbol = stateScope.resolve("y0", VariableSymbol.KIND);
    assertTrue(y0Symbol.isPresent());

    // retrieve parameter block
    final Scope parameterScope = astNeuronDecorator.getParameterBlock().get().getEnclosingScope().get();
    assertSame(stateScope, parameterScope);
    assertTrue(parameterScope.resolve("y0", VariableSymbol.KIND).isPresent());
    assertTrue(parameterScope.resolve("C_m", VariableSymbol.KIND).isPresent());

    // retrieve dynamics block
    final Scope dynamicsScope = astNeuronDecorator.getUpdateBlocks().get(0).getBlock().getEnclosingScope().get();

    final Optional<VariableSymbol> newVarInMethodSymbol
        = dynamicsScope.resolve("newVarInMethod", VariableSymbol.KIND);
    assertTrue(newVarInMethodSymbol.isPresent());
    assertTrue(newVarInMethodSymbol.get().getType().equals(PredefinedTypes.getRealType()));


  }

  @Test
  public void testShadowingOfVariablesInMethods() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTNeuron astNeuronDecorator = (root.getNeurons().get(0));

    final Optional<ASTBlockWithVariables> neuronState = astNeuronDecorator.getStateBlock();
    assertTrue(neuronState.isPresent());
    final Optional<VariableSymbol> testVarFromParameter =
        neuronState.get().getEnclosingScope().get().resolve("scopeTestVar",
            VariableSymbol.KIND);

    // check the symbol from parameter block
    assertTrue(testVarFromParameter.isPresent());
    assertTrue(testVarFromParameter.get().getType().equals(PredefinedTypes.getStringType()));

    // check the symbol in function block
    final Optional<ASTFunction> scopeTestingFunction = astNeuronDecorator
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
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
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
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);

    final Optional<MethodSymbol> fromGlobalScope
        = scopeCreator.getGlobalScope().resolve("exp", MethodSymbol.KIND);
    assertTrue(fromGlobalScope.isPresent());


    final Optional<MethodSymbol> fromModelScope = modelScope.resolve("exp", MethodSymbol.KIND);
    assertTrue(fromModelScope.isPresent());

    final Optional<MethodSymbol> withPredicate
        = resolveMethod("exp", Lists.newArrayList("real"), modelScope);
    assertTrue(withPredicate.isPresent());

    Optional<MethodSymbol> I_sumOptional = resolveMethod(PredefinedFunctions.CURR_SUM, Lists.newArrayList("pA", "real"), modelScope);
    assertTrue(I_sumOptional.isPresent());
    I_sumOptional = resolveMethod(PredefinedFunctions.CURR_SUM, Lists.newArrayList("nS", "Buffer"), modelScope);
    assertFalse(I_sumOptional.isPresent());
    I_sumOptional = resolveMethod(PredefinedFunctions.CURR_SUM, Lists.newArrayList("pA", "Buffer"), modelScope);
    assertFalse(I_sumOptional.isPresent());

    Optional<MethodSymbol> Cond_sumOptional = resolveMethod(PredefinedFunctions.COND_SUM, Lists.newArrayList("nS", "real"), modelScope);
    assertTrue(Cond_sumOptional.isPresent());
    Cond_sumOptional = resolveMethod(PredefinedFunctions.COND_SUM, Lists.newArrayList("pA", "Buffer"), modelScope);
    assertFalse(Cond_sumOptional.isPresent());
    Cond_sumOptional = resolveMethod(PredefinedFunctions.COND_SUM, Lists.newArrayList("nS", "Buffer"), modelScope);
    assertFalse(Cond_sumOptional.isPresent());
  }


  @Test
  public void testResolvingOfPredefinedFunctions() throws IOException {
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());

    scopeCreator.runSymbolTableCreator(root);

    final ASTNeuron astNeuronDecorator = (root.getNeurons().get(0));

    final Optional<ASTBlockWithVariables> neuronState = astNeuronDecorator.getStateBlock();
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
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
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
  public void testRecognitionOfConductanceBasedBuffers() {
    final ASTNESTMLCompilationUnit root = parseNestmlModel(MODEL_FILE_NAME);
    assertEquals(1, root.getNeurons().size());
    scopeCreator.runSymbolTableCreator(root);

    final List<VariableSymbol> spikeBuffers = root.getNeurons().get(0).getSpikeBuffers();
    assertTrue(spikeBuffers.size() == 1);
    assertTrue(spikeBuffers.get(0).isConductanceBased());
  }

}
