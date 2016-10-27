/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import com.google.common.base.Preconditions;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTParameter;
import org.nest.nestml._ast.ASTUSE_Stmt;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Optional;

import static org.abego.treelayout.internal.util.Contract.checkState;
import static org.nest.utils.AstUtils.computeTypeName;

/**
 * Only predefined types must be used in a declaration.
 *
 * @author ippen, plotnikov
 */
public class InvalidTypesInDeclaration implements
    NESTMLASTUSE_StmtCoCo,
    SPLASTDeclarationCoCo,
    NESTMLASTFunctionCoCo {
  public static final String ERROR_CODE = "NESTML_INVALID_TYPES_DECLARATION";

  @Override
  public void check(final ASTDeclaration astDeclaration) {
    String typeName = computeTypeName(astDeclaration.getDatatype());

    final Optional<? extends Scope> enclosingScope = astDeclaration.getEnclosingScope();
    Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + astDeclaration);
    Optional<TypeSymbol> type = enclosingScope.get().resolve(typeName, TypeSymbol.KIND);
    checkIfValidType(astDeclaration, typeName, type);

  }

  @Override
  public void check(final ASTFunction astFunction) {
    String typeName;
    // check parameter types
    if (astFunction.getParameters().isPresent()) {
      for (ASTParameter par : astFunction.getParameters().get().getParameters()) {
        typeName = computeTypeName(par.getDatatype());

        Optional<? extends Scope> enclosingScope = astFunction.getEnclosingScope();
        Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + astFunction);
        Optional<TypeSymbol> type = enclosingScope.get().resolve(typeName, TypeSymbol.KIND);

        checkIfValidType(astFunction, typeName, type);

      }

      // check return type
      if (astFunction.getReturnType().isPresent()) {
        typeName = computeTypeName(astFunction.getReturnType().get());

        final Optional<? extends Scope> enclosingScope = astFunction.getEnclosingScope();
        Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + astFunction);
        final Optional<TypeSymbol> type = enclosingScope.get().resolve(typeName, TypeSymbol.KIND);
        checkIfValidType(astFunction, typeName, type);

        //doCheck(type.get(), fun.getReturnType().get(), true);
      }
    }

  }

  private void checkIfValidType(ASTNode astNode, String typeName, Optional<TypeSymbol> type) {
    if (!type.isPresent() || type.isPresent() && type.get().getName().endsWith("Logger")) {
      NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
      String msg = errorStrings.getErrorMsg(this,typeName);

      Log.error(msg, astNode.get_SourcePositionStart());
    }
  }

  @Override
  public void check(ASTUSE_Stmt astUseStmt) {
    String typeName = Names.getQualifiedName(astUseStmt.getName().getParts());
    Optional<? extends Scope> enclosingScope = astUseStmt.getEnclosingScope();
    checkState(enclosingScope.isPresent(),
        "There is no scope assigned to the AST node at: " + astUseStmt.get_SourcePositionStart());
    final Optional<NeuronSymbol> type = enclosingScope.get().resolve(typeName, NeuronSymbol.KIND);

    if (!type.isPresent()) {
      NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
      final String msg = errorStrings.getErrorMsg(this,typeName);

      Log.error(msg, astUseStmt.get_SourcePositionStart());
    }

  }


}
