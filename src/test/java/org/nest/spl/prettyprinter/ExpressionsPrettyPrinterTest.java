/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.prettyprinter;

import org.junit.Test;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests prettyprinter on the most available models in test resources.
 *
 * @author (last commit) plotnikov
 * @since 0.0.1
 */
public class ExpressionsPrettyPrinterTest {
  private final SPLParser splFileParser = new SPLParser();
  private final ExpressionsPrettyPrinter expressionsPrettyPrinter = new ExpressionsPrettyPrinter();
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void testThatPrettyPrinterProducesParsableOutput() throws IOException {

    final Optional<ASTSPLFile> root = splFileParser.parse
        ("src/test/resources/org/nest/spl/parsing/complexExpressions.simple");
    assertTrue(root.isPresent());

    // TODO write frontend manager for the cocos and check them on the model
    SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH, typesFactory);
    splScopeCreator.runSymbolTableCreator(root.get());// do I need symbol table for the pretty printer
    System.out.println(expressionsPrettyPrinter
        .print(root.get().getBlock().getStmts().get(4).getSimple_Stmt().get()
            .getSmall_Stmts().get(0).getDeclaration().get().getExpr().get()));
    // TODO
    //System.out.println(expressionsPrettyPrinter.print(root.get().getBlock().getStmts().get(6).getSimple_Stmt().get()
    //    .getSmall_Stmts().get(0).getDeclaration().get().getExpr().get()));

  }
}
