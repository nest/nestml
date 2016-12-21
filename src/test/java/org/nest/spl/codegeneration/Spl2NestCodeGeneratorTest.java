/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.codegeneration;

import de.monticore.generating.templateengine.GlobalExtensionManagement;
import org.junit.Assert;
import org.junit.Test;
import org.nest.codegeneration.Spl2NestCodeGenerator;
import org.nest.codegeneration.helpers.ASTDeclarations;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTBlock;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.utils.AstUtils;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests the generator fot the SPL sub-language
 *
 * @author plotnikov
 */
public class Spl2NestCodeGeneratorTest {

  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String OUTPUT_FOLDER = "target";

  private GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

  @Test
  public void invokeSPL2NESTGenerator() throws IOException {
    final SPLParser p = new SPLParser();
    final File outputFolder = new File(OUTPUT_FOLDER);
    final String packageName = "org.nest.spl.parsing";
    final String modelName = "decl";
    final String fullQualifiedModelname = packageName + "." + modelName;

    final Path outputFile = Paths.get(fullQualifiedModelname.replaceAll("\\.", File.separator));
    Optional<ASTSPLFile> root = p.parse(TEST_MODEL_PATH + File.separator + fullQualifiedModelname.replaceAll("\\.", File.separator) + ".simple");
    Assert.assertTrue(root.isPresent());

    final SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
    splScopeCreator.runSymbolTableCreator(root.get());

    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final Spl2NestCodeGenerator generator = new Spl2NestCodeGenerator(glex, outputFolder);
    final ASTDeclarations declarations = new ASTDeclarations();
    glex.setGlobalValue("declarations", declarations);

    // tests code generation for a spldeclaration
    final Optional<ASTDeclaration> wahrDeclaration = root.get()
        .getBlock().getStmts().get(0)
        .getSmall_Stmt().get()
        .getDeclaration();
    assertTrue(wahrDeclaration.isPresent());
    generator.handle(wahrDeclaration.get(), outputFile);

    // tests code generation for a spldeclaration with an expression
    final Optional<ASTDeclaration> realDeclaration = root.get()
        .getBlock().getStmts().get(2)
        .getSmall_Stmt().get()
        .getDeclaration();
    assertTrue(realDeclaration.isPresent());
    generator.handle(realDeclaration.get(), outputFile);


    // tests code generation for an assignment
    // retrieves: intVar = 2
    final ASTAssignment intVarAssignment = AstUtils.getAll(root.get(), ASTAssignment.class).get(0);
    generator.handle(intVarAssignment, outputFile);

    // tests code generation for the entire Block
    final ASTBlock block = root.get().getBlock();
    generator.handle(block, outputFile);
  }

}
