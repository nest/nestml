package org.nest.nestml._parser;

import de.monticore.antlr4.MCConcreteParser;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.antlr.v4.runtime.RecognitionException;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.utils.AstUtils;
import org.nest.utils.LogHelper;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static org.junit.Assert.*;
import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;

/**
 * Tests the method which set artifact and package name according to the file name and corresponding
 *
 *
 * @author plonikov
 */
public class NESTMLParserTest extends ModelbasedTest {
  private static final String PARSER_INPUT = "src/test/resources/parser/";

  @Test
  public void testAllModels() {
    // ignore all models, in an folder with an 'parser.unparsable' infix
    final List<Path> testModels = collectNESTMLModelFilenames(Paths.get("src/test/resources/"))
        .stream()
        .filter( path -> !path.toString().contains("unparsable"))
        .collect(Collectors.toList());

    for (final Path path:testModels) {
      System.out.println(path.toString());
      parseNestmlModel(path.toString());
    }
  }

  @Test
  public void testNonExistentType() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse("src/test/resources/parser/unparsable/wrongTypes.nestml");
    assertFalse(ast.isPresent());
    List<Finding> findings = LogHelper.getModelErrors(Log.getFindings());
    assertEquals(2, findings.size());
  }

  @Test
  public void testMultipleVariablesWithSameName() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse("src/test/resources/parser/unparsable/multipleVariablesWithSameName.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    assertTrue(LogHelper.getModelErrors(Log.getFindings()).size() > 0);
  }

  @Test
  public void testCommentsExtraction() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse("/home/nestml/repositories/nestml/target/integration/iaf_neuron_nestml.tmp");
    //final Optional<ASTNESTMLCompilationUnit> ast = parser.parse(PARSER_INPUT + "comments.nestml");
    assertTrue(ast.isPresent());
    final List<ASTDeclaration> declarations = AstUtils.getAll(ast.get(), ASTDeclaration.class);
    for (final ASTDeclaration declaration:declarations) {
      System.out.println(declaration.getVars().get(0).toString() + ":  " + declaration.getDocString());

    }

  }

  @Test
  public void testAddingTrivialEquations() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse(PARSER_INPUT + "adding_odes.nestml");
    assertTrue(ast.isPresent());
    final List<ASTEquation> equations = AstUtils.getAll(ast.get(), ASTEquation.class);
    System.out.println(NESTMLPrettyPrinter.print(ast.get()));
    assertEquals(6, equations.size());

  }

  public Optional<ASTExpr> parse(String input) throws RecognitionException, IOException {
    final NESTMLParser parser = new NESTMLParser();
    parser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    return parser.parseExpr(new StringReader(input));
  }

  @Test
  public void testPlus() throws IOException {
    Optional<ASTExpr> res = parse("-a");
    assertTrue(res.isPresent());
    assertEquals("a", res.get().getTerm().get().getVariable().get().toString());
    assertTrue(res.get().isUnaryMinus());

  }


  @Test
  public void testNumber() throws IOException {
    final Optional<ASTExpr> res = parse("-11");
    //System.out.println(createPrettyPrinterForTypes().prettyprint(res.get().getTerm().get()));
    assertTrue(res.get().isUnaryMinus());

  }

  @Test
  public void rightAssociativeExpression() throws IOException {
    final NESTMLParser splParser = new NESTMLParser();
    splParser.setParserTarget(MCConcreteParser.ParserExecution.EOF);
    final Optional<ASTExpr> result = splParser.parseExpr(new StringReader("e1**e2**e3"));

    // asserts that the parse tree is built as e1**(e2**e3), e.g. in a right associative way
    final String base = result.get().getBase().get().getVariable().get().toString();
    assertEquals("e1", base);
    assertTrue(result.get().getExponent().get().isPow());
  }
}