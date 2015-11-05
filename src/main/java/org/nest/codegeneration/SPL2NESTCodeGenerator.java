/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import org.nest.codegeneration.helpers.NESTMLDeclarations;
import org.nest.codegeneration.helpers.SPLForNodes;
import org.nest.codegeneration.helpers.SPLVariableGetterSetterHelper;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTBlock;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.nio.file.Path;

/**
 * Code-Generator for the SPL sublanguage. Templates are reused in the NESTML generator.
 * @author plotnikov
 */
public class SPL2NESTCodeGenerator {
  public static final String DECLARATION_TEMPLATE = "org.nest.spl.Declaration";
  public static final String ASSIGNMENT_TEMPLATE = "org.nest.spl.Assignment";
  public static final String BLOCK_TEMPLATE = "org.nest.spl.Block";

  final private GlobalExtensionManagement glex;
  private final GeneratorSetup setup;
  private final GeneratorEngine generator;

  public SPL2NESTCodeGenerator(
      final GlobalExtensionManagement glex,
      final PredefinedTypesFactory typesFactory,
      final File outputDirectory) {
    this.glex = glex;
    this.setup = new GeneratorSetup(outputDirectory);

    final ExpressionsPrettyPrinter prettyPrinter = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("assignmentHelper", new SPLVariableGetterSetterHelper());
    glex.setGlobalValue("declarations", new NESTMLDeclarations(typesFactory) );
    glex.setGlobalValue("expressionsPrinter", prettyPrinter);
    glex.setGlobalValue("forDeclarationHelper", new SPLForNodes());

    setup.setGlex(glex);
    generator = new GeneratorEngine(setup);
  }

  public void handle(final ASTDeclaration astDeclaration, final Path outputFile) {
    generator.generate(DECLARATION_TEMPLATE, outputFile, astDeclaration);
  }

  public void handle(final ASTAssignment astAssignment, final Path outputFile) {
    generator.generate(ASSIGNMENT_TEMPLATE, outputFile, astAssignment);
  }

  public void handle(ASTBlock astBlock, Path outputFile) {
    generator.generate(BLOCK_TEMPLATE, outputFile, astBlock);
  }
}
