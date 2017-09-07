/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import org.junit.Assert;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

/**
 * @author plotnikov
 */
public class AstUtilsTest extends ModelbasedTest {
  private static final String PSC_MODEL_WITH_ODE = "models/ht_neuron.nestml";

  @Test
  public void testComputationAliases() {
    final ASTNESTMLCompilationUnit astCompilationUnit = parseAndBuildSymboltable(PSC_MODEL_WITH_ODE);
    Assert.assertTrue(astCompilationUnit.getNeurons().get(0).getOdeBlock().isPresent());

    final List<VariableSymbol> aliasesIn = AstUtils.getAliasSymbols(astCompilationUnit.getNeurons().get(0).getOdeBlock().get());
    final Optional<VariableSymbol> testant = aliasesIn.stream().filter(alias -> alias.getName().equals("I_syn_ampa")).findAny();
    Assert.assertTrue(testant.isPresent());
  }
}