package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTDerivative;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 *
 * @author plotnikov
 */
public class NamesTest extends ModelbasedTest {
  private static final String PSC_MODEL_WITH_ODE = "models/iaf_cond_alpha.nestml";
  private final Names names = new Names();
  @Test
  public void testComputationOfInverseFunction() {
    final ASTNESTMLCompilationUnit root = parseNestmlModel(PSC_MODEL_WITH_ODE);
    final Scope modelScope = scopeCreator.runSymbolTableCreator(root);
    final Optional<NeuronSymbol> neuronTypeOptional = modelScope.resolve(
        "iaf_cond_alpha_implicit",
        NeuronSymbol.KIND);
    assertTrue(neuronTypeOptional.isPresent());
    final Optional<VariableSymbol> Dg_in = neuronTypeOptional.get().getSpannedScope().resolve("g_in'", VariableSymbol.KIND);
    assertTrue(Dg_in.isPresent());

    assertEquals("__D_g_in", names.name(Dg_in.get()));
    assertEquals("set___D_g_in", names.setter(Dg_in.get()));
    assertEquals("get___D_g_in", names.getter(Dg_in.get()));

    final Optional<ASTDerivative> derivative = AstUtils
        .getAll(root, ASTDerivative.class)
        .stream()
        .filter(tmp -> tmp.toString().equals("g_in''"))
        .findAny();

    assertTrue(derivative.isPresent());
    assertEquals("__DD_g_in", names.name(derivative.get()));
  }
}