/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import org.junit.Assert;
import org.junit.Test;
import org.nest.base.GenerationBasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 *
 *
 * @author plotnikov
 */
public class AliasInverterTest extends GenerationBasedTest {
  private static final String PSC_MODEL_WITH_ODE = "models/iaf_psc_alpha.nestml";

  @Test
  public void testComputationOfInverseFunction() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_WITH_ODE);
    scopeCreator.runSymbolTableCreator(root);

    VariableSymbol v_alias = root.getNeurons().get(0)
        .getBody()
        .getParameterSymbols()
        .stream()
        .filter(varialbe -> varialbe.getName().equals("tau_syn_in"))
        .findAny()
        .get();
    Assert.assertFalse(AliasInverter.isInvertableExpression(v_alias.getDeclaringExpression().get()));

    VariableSymbol v_m_alias = root.getNeurons().get(0)
        .getBody()
        .getStateAliasSymbols()
        .stream()
        .filter(alias -> alias.getName().equals("V_m"))
        .findAny()
        .get();

    Assert.assertTrue(AliasInverter.isInvertableExpression(v_m_alias.getDeclaringExpression().get()));

    final String inversedOperation = AliasInverter.inverseOperator(v_m_alias.getDeclaringExpression().get());
    assertEquals("-", inversedOperation);


    final List<VariableSymbol> offests = root.getNeurons().get(0)
        .getBody()
        .getAllOffsetVariables();
    assertTrue(offests.size() == 1);
  }

  @Test
  public void testRelativeDefinition() {
    final ASTNESTMLCompilationUnit root = parseNESTMLModel(PSC_MODEL_WITH_ODE);
    scopeCreator.runSymbolTableCreator(root);

    VariableSymbol v_alias = root.getNeurons().get(0)
        .getBody()
        .getStateSymbols()
        .stream()
        .filter(varialbe -> varialbe.getName().equals("V_m"))
        .findAny()
        .get();
    Assert.assertFalse(AliasInverter.isRelativeExpression(v_alias.getDeclaringExpression().get()));

    VariableSymbol v_reset = root.getNeurons().get(0)
        .getBody()
        .getParameterSymbols()
        .stream()
        .filter(alias -> alias.getName().equals("V_reset"))
        .findAny()
        .get();

    Assert.assertTrue(AliasInverter.isRelativeExpression(v_reset.getDeclaringExpression().get()));

    final String inversedOperation = AliasInverter.inverseOperator(v_reset.getDeclaringExpression().get());
    assertEquals("+", inversedOperation);

    final List<VariableSymbol> offests = root.getNeurons().get(0)
        .getBody()
        .getAllOffsetVariables();
    assertTrue(offests.size() == 1);
  }

}