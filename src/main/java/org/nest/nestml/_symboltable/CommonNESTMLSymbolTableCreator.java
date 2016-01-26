/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.CommonSymbolTableCreator;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTVar_Block;

import java.util.Optional;

/**
 * The implementation of the symboltable creator.
 * Implements required methods to compute packagename, current alias declaration
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class CommonNESTMLSymbolTableCreator
    extends CommonSymbolTableCreator
    implements NESTMLSymbolTableCreator {
  private ASTNESTMLCompilationUnit root;
  private Optional<ASTAliasDecl> astAliasDeclaration = Optional.empty();
  private Optional<ASTVar_Block> astVariableBlockType = Optional.empty();

  public CommonNESTMLSymbolTableCreator(
      final ResolverConfiguration resolverConfig,
      final MutableScope enclosingScope) {
    super(resolverConfig, enclosingScope);
  }

  @Override
  public void setRoot(ASTNESTMLCompilationUnit root) {
    this.root = root;
  }

  @Override
  public ASTNESTMLCompilationUnit getRoot() {
    return root;
  }

  @Override
  public void setAliasDeclaration(final Optional<ASTAliasDecl> astAliasDeclaration) {
    this.astAliasDeclaration = astAliasDeclaration;
  }

  @Override
  public Optional<ASTAliasDecl> getAliasDeclaration() {
    return astAliasDeclaration;
  }

  @Override public void setVariableBlockType(Optional<ASTVar_Block> variableBlockType) {
    astVariableBlockType = variableBlockType;
  }

  @Override public Optional<ASTVar_Block> getVariableBlockType() {
    return astVariableBlockType;
  }

}
