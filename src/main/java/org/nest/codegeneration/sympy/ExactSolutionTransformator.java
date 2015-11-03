/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.apache.commons.io.FileUtils;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;

import java.io.File;
import java.io.IOException;
import java.util.List;

/**
 * Test the overall script generation and evaluation of the generated scripts
 *
 * @author plotnikov
 */
public class ExactSolutionTransformator {

  final SymPyOutput2NESTMLConverter symPyOutput2NESTMLConverter = new SymPyOutput2NESTMLConverter();

  public void addPropagatorMatrixAndPrint(
      final ASTNESTMLCompilationUnit root,
      final String pathToMatrix,
      final String outputPath) {

    final List<ASTAliasDecl> propagatorMatrix = symPyOutput2NESTMLConverter
        .createDeclarationASTs(pathToMatrix);

    addVariablesToInternalBlock(root, propagatorMatrix);

    printModelToFile(root, outputPath);
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

  private void addVariablesToInternalBlock(
      final ASTNESTMLCompilationUnit root,
      final List<ASTAliasDecl> propagatorMatrix) {
    final ASTBodyDecorator astBodyDecorator
        = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    propagatorMatrix.forEach(astBodyDecorator::addToInternalBlock);
  }

}
