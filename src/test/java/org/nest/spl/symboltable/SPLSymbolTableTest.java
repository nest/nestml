/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import de.monticore.symboltable.GlobalScope;
import org.junit.Test;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Test resolving of variables and functions from a SPL program.
 *
 * @author plotnikov
 */
public class SPLSymbolTableTest {
  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void testCreationOfSymtabAndResolvingOfSymbols() throws IOException {

    final SPLParser p = new SPLParser();
    final Optional<ASTSPLFile> root = p.parse(
        "src/test/resources/org/nest/spl/symboltable/decl.simple");
    assertTrue(root.isPresent());


    SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH, typesFactory);
    splScopeCreator.runSymbolTableCreator(root.get());

    final GlobalScope globalScope = splScopeCreator.getGlobalScope();
    globalScope.resolve("Time.steps", NESTMLMethodSymbol.KIND);
    Optional<NESTMLVariableSymbol> variable = globalScope.resolve("org.nest.spl.symboltable.decl.decl", NESTMLVariableSymbol.KIND);
    assertTrue(variable.isPresent());

    // resolve implicit types
    for (NESTMLTypeSymbol type: splScopeCreator.getTypesFactory().getTypes()) {
      Optional<NESTMLTypeSymbol> resolvedType = globalScope.resolve(type.getFullName(), NESTMLTypeSymbol.KIND);
      assertTrue("Cannot resolve the type: " + type.getFullName(), resolvedType.isPresent());
    }

  }

}
