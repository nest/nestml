/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import de.monticore.symboltable.*;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLVisitor;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.ArrayList;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static java.util.Objects.requireNonNull;

/**
 * Visitor that creates symbols for SPLTypes, SPLVariables from an SPL model.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
interface SPLSymbolTableCreator extends SymbolTableCreator, SPLVisitor {

  String LOGGER_NAME = SPLSymbolTableCreator.class.getName();

  PredefinedTypesFactory getTypesFactory();
  /**
   * Creates the symbol table starting from the <code>rootNode</code> and returns the first scope
   * that was created.
   *
   * @param rootNode the root node
   * @return the first scope that was created
   */
  default Scope createFromAST(final ASTSPLNode rootNode) {
    requireNonNull(rootNode);
    rootNode.accept(this);
    return getFirstCreatedScope();
  }

  @Override
  default void visit(final ASTSPLFile ast) {
    final String fullName = Names.getQualifiedName(ast.getModuleDefinitionStatement().getModuleName().getParts());
    final String packageName = Names.getQualifier(fullName);
    final String modelName = Names.getSimpleName(fullName);

    final MutableScope artifactScope = new ArtifactScope(Optional.empty(), packageName + "." + modelName, new ArrayList<>());
    putOnStack(artifactScope);
    ast.setEnclosingScope(artifactScope);

    final String msg = String.format("Adds new scope for the separate SPL model: %s", modelName);
    Log.info(msg, LOGGER_NAME);
  }

  @Override
  default void endVisit(final ASTSPLFile root) {
    removeCurrentScope();

    setEnclosingScopeOfNodes(root);
    Log.info("Sets scopes on all ASTs.", LOGGER_NAME);
  }

  @Override
  default void visit(final ASTCompound_Stmt astCompoundStmt) {
    final CommonScope shadowingScope = new CommonScope(true);
    putOnStack(shadowingScope);

  }

  @Override
  default void endVisit(final ASTCompound_Stmt astCompoundStmt) {
    removeCurrentScope();
  }

  @Override
  default void visit(final ASTDeclaration astDeclaration) {
    for (String variableName : astDeclaration.getVars()) {
      NESTMLVariableSymbol variable = new NESTMLVariableSymbol(variableName);
      String typeName = computeTypeName(astDeclaration);
      variable.setAstNode(astDeclaration);
      variable.setType(getTypesFactory().getType(typeName)); // if exists better choice?

      // handle ST infrastructure
      putInScopeAndLinkWithAst(variable, astDeclaration);

      Log.info("Creates a variable: " + variableName + " with the type: " + typeName, LOGGER_NAME);
    }

  }

  /**
   * Computes the typename for the declaration ast. It is defined in one of the grammar
   * alternatives.
   */
  default String computeTypeName(final ASTDeclaration astDeclaration) {
    String typeName = null;
    if (astDeclaration.getType().isPresent()) {
      typeName = astDeclaration.getType().get().toString();
    }
    else if (astDeclaration.getPrimitiveType().isPresent()) {
      typeName = astDeclaration.getPrimitiveType().get().toString();
    }
    else {
      checkState(false, "Is not possible through the grammar construction.");
    }
    return typeName;
  }

}
