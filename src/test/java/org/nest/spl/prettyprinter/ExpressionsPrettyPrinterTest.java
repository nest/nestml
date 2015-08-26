package org.nest.spl.prettyprinter;

import org.junit.Test;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLFileMCParser;
import org.nest.spl._parser.SPLParserFactory;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Created by user on 02.06.15.
 */
public class ExpressionsPrettyPrinterTest {
  private final SPLFileMCParser splFileParser = SPLParserFactory.createSPLFileMCParser();
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
