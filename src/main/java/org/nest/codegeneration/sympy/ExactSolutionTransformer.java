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

/**
 * Manages the overall script generation and evaluation of the generated scripts
 *
 * @author plotnikov
 */
public class ExactSolutionTransformer {

  final Sympy2NESTMLConverter converter2NESTML = new Sympy2NESTMLConverter();

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   * @param root
   * @param pathToP00File
   * @param outputModelFile
   */
  public void addP00(
      final ASTNESTMLCompilationUnit root,
      final String pathToP00File,
      final String outputModelFile) {

    final ASTAliasDecl p00Declaration = converter2NESTML.convertDeclaration(pathToP00File);

    addToInternalBlock(root, p00Declaration);

    printModelToFile(root, outputModelFile);
  }

  /**
   * Adds the declaration of the P00 value to the nestml model. Note: very NEST specific.
   * @param root
   * @param pathPSCInitialValueFile
   * @param outputModelFile
   */
  public void addPSCInitialValue(
      final ASTNESTMLCompilationUnit root,
      final String pathPSCInitialValueFile,
      final String outputModelFile) {

    final ASTAliasDecl pscInitialValue = converter2NESTML.convertDeclaration(pathPSCInitialValueFile);

    addToInternalBlock(root, pscInitialValue);

    printModelToFile(root, outputModelFile);
  }


  private void printModelToFile(
      final ASTNESTMLCompilationUnit astNestmlCompilationUnit,
      final String outputModelFile) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    astNestmlCompilationUnit.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputModelFile);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
     throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputModelFile, e);
    }
  }

  private void addToInternalBlock(
      final ASTNESTMLCompilationUnit root,
      final ASTAliasDecl declaration) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(root.getNeurons().get(0).getBody());
    astBodyDecorator.addToInternalBlock(declaration);
  }

}
