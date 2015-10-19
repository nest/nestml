/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.codegeneration;

import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.Names;
import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.codegeneration.NESTMLDeclarations;
import org.nest.codegeneration.SPL2NESTCodeGenerator;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTBlock;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLFileMCParser;
import org.nest.spl._parser.SPLParserFactory;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.Names.getPathFromQualifiedName;
import static de.se_rwth.commons.Names.getSimpleName;
import static org.junit.Assert.assertTrue;

@Ignore
public class SPL2NESTCodeGeneratorTest {

  private static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String OUTPUT_FOLDER = "target";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  private GlobalExtensionManagement createGLEXConfiguration() {

    return new GlobalExtensionManagement();
  }

  @Test
  public void invokeSPL2NESTGenerator() throws IOException {
    final SPLFileMCParser p = SPLParserFactory.createSPLFileMCParser();
    final File outputFolder = new File(OUTPUT_FOLDER);
    final String packageName = "org.nest.spl.codegeneration";
    final String modelName = "decl";
    final String fullQualifiedModelname = packageName + "." + modelName;
    final Path outputFile = Paths.get(fullQualifiedModelname);

    final String pathToModel = Paths.get(
        TEST_MODEL_PATH,
        getPathFromQualifiedName(fullQualifiedModelname),
        getSimpleName(fullQualifiedModelname) + ".simple").toString();

    final Optional<ASTSPLFile> root = p.parse(pathToModel);
    Assert.assertTrue(root.isPresent());

    final SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH, typesFactory);
    splScopeCreator.runSymbolTableCreator(root.get());

    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final SPL2NESTCodeGenerator generator = new SPL2NESTCodeGenerator(glex, typesFactory, outputFolder);
    final NESTMLDeclarations declarations = new NESTMLDeclarations(splScopeCreator.getTypesFactory());
    glex.setGlobalValue("declarations", declarations);

    // tests code generation for a spldeclaration
    final Optional<ASTDeclaration> wahrDeclaration = root.get()
        .getBlock().getStmts().get(0)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getDeclaration();
    assertTrue(wahrDeclaration.isPresent());
    generator.handle(wahrDeclaration.get(), outputFile);

    // tests code generation for a spldeclaration with an expression
    final Optional<ASTDeclaration> realDeclaration = root.get()
        .getBlock().getStmts().get(2)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getDeclaration();
    assertTrue(realDeclaration.isPresent());
    generator.handle(realDeclaration.get(), outputFile);

    // tests code generation for an assignment
    final Optional<ASTAssignment> intVarAssignment = root.get()
        .getBlock().getStmts().get(3)
        .getSimple_Stmt().get()
        .getSmall_Stmts().get(0)
        .getAssignment();
    assertTrue(intVarAssignment.isPresent());
    generator.handle(intVarAssignment.get(), outputFile);

    // tests code generation for the entire Block
    final ASTBlock block = root.get().getBlock();
    generator.handle(block, outputFile);
  }

}
