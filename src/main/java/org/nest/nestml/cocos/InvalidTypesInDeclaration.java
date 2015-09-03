/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import de.monticore.ast.ASTCNode;
import de.monticore.ast.ASTNode;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;
import org.nest.nestml._cocos.NESTMLASTUSE_StmtCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.utils.ASTNodes;

import java.util.Optional;

import static org.abego.treelayout.internal.util.Contract.checkState;

/**
 * Only predefined types must be used in a declaration.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class InvalidTypesInDeclaration implements
    NESTMLASTUSE_StmtCoCo,
    SPLASTDeclarationCoCo,
    NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "NESTML_INVALID_TYPES_DECLARATION";


  @Override
  public void check(final ASTDeclaration astDeclaration) {

    if (astDeclaration.getType().isPresent()) {
      String typeName = Names.getQualifiedName(astDeclaration.getType().get().getParts());

      final Optional<? extends Scope> enclosingScope = astDeclaration.getEnclosingScope();
      Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + astDeclaration);
      Optional<NESTMLTypeSymbol> type = enclosingScope.get().resolve(typeName, NESTMLTypeSymbol.KIND);
      checkIfValidType(astDeclaration, typeName, type);

    }

  }

  @Override
  public void check(final ASTFunction astFunction) {
    String typeName;
    // check parameter types
    if (astFunction.getParameters().isPresent()) {
      for (ASTParameter par : astFunction.getParameters().get().getParameters()) {
        typeName = Names.getQualifiedName(par.getType().getParts());

        Optional<? extends Scope> enclosingScope = astFunction.getEnclosingScope();
        Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + astFunction);
        Optional<NESTMLTypeSymbol> type = enclosingScope.get().resolve(typeName, NESTMLTypeSymbol.KIND);

        checkIfValidType(astFunction, typeName, type);

      }

      // check return type
      if (astFunction.getReturnType().isPresent()) {
        typeName = Names.getQualifiedName(astFunction.getReturnType().get().getParts());

        final Optional<? extends Scope> enclosingScope = astFunction.getEnclosingScope();
        Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + astFunction);
        final Optional<NESTMLTypeSymbol> type = enclosingScope.get().resolve(typeName, NESTMLTypeSymbol.KIND);
        checkIfValidType(astFunction, typeName, type);

        //doCheck(type.get(), fun.getReturnType().get(), true);
      }
    }

  }

  public void checkIfValidType(ASTNode astNode, String typeName, Optional<NESTMLTypeSymbol> type) {
    if (!type.isPresent() || type.isPresent() && type.get().getName().endsWith("Logger")) {
      final String msgPredefined = "The type '%s' is a neuron/component. No neurons/components allowed " +
          "in this place. Use the use-statement.";
      Log.error(ERROR_CODE + ":" + String.format(msgPredefined, typeName),
          astNode.get_SourcePositionStart());
    }
  }

  @Override
  public void check(ASTUSE_Stmt astUseStmt) {
    String typeName = Names.getQualifiedName(astUseStmt.getName().getParts());
    Optional<? extends Scope> enclosingScope = astUseStmt.getEnclosingScope();
    checkState(enclosingScope.isPresent(),
        "There is no scope assigned to the AST node at: " + astUseStmt.get_SourcePositionStart());
    final Optional<NESTMLNeuronSymbol> type = enclosingScope.get().resolve(
        typeName, NESTMLNeuronSymbol.KIND);

    if (!type.isPresent()) {
      final String msgPredefined = "The type '%s' is a neuron/component. No neurons/components allowed " +
          "in this place. Use the use-statement.";
      Log.error(ERROR_CODE + String.format(msgPredefined, typeName),
          astUseStmt.get_SourcePositionStart());
    }

  }


}
