package org.nest.codegeneration.sympy;

import org.apache.commons.io.FileUtils;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Optional;

/**
 * Created by user on 12.06.15.
 */
public class ModelConverter {

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();

  final Sympy2NESTMLConverter sympy2NESTMLConverter = new Sympy2NESTMLConverter();

  public void addPropagatorMatrixAndPrint(
      final String pathToModel,
      final String pathToMatrix,
      final String outputPath) {
    final Optional<ASTNESTMLCompilationUnit> root = parseModel(pathToModel);

    final List<ASTAliasDecl> propagatorMatrix = sympy2NESTMLConverter.convertMatrixFile2NESTML(pathToMatrix);

    addVariablesToInternalBlock(root, propagatorMatrix);

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());
    printModelToFile(root.get(), outputPath);
  }

  private void printModelToFile(
      final ASTNESTMLCompilationUnit astNestmlCompilationUnit,
      final String outputPath) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    astNestmlCompilationUnit.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputPath);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
     throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputPath, e);
    }
  }

  private void addVariablesToInternalBlock(Optional<ASTNESTMLCompilationUnit> root,
      List<ASTAliasDecl> propagatorMatrix) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.get().getNeurons().get(0).getBody());
    propagatorMatrix.forEach(astBodyDecorator::addToInternalBlock);
  }

  private Optional<ASTNESTMLCompilationUnit> parseModel(String pathToModel)  {
    try {
      return p.parse(pathToModel);
    }
    catch (final IOException e) {
      throw new RuntimeException("Cannot parse the NESTML model: " + pathToModel, e);
    }

  }

}
