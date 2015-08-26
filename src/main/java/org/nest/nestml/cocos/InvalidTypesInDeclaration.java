package org.nest.nestml.cocos;


import com.google.common.base.Preconditions;
import de.monticore.ast.ASTCNode;
import de.monticore.ast.ASTNode;
import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
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

public class InvalidTypesInDeclaration implements
    NESTMLASTUSE_StmtCoCo,
    SPLASTDeclarationCoCo,
    NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "NESTML_INVALID_TYPES_DECLARATION";


  @Override
  public void check(ASTDeclaration decl) {

    if (decl.getType().isPresent()) {
      String typeName = Names.getQualifiedName(decl.getType().get().getParts());

      final Optional<? extends Scope> enclosingScope = decl.getEnclosingScope();
      Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + decl);
      Optional<NESTMLTypeSymbol> type = enclosingScope.get().resolve(typeName, NESTMLTypeSymbol.KIND);
      checkIfValidType(decl, typeName, type);

    }

  }

  @Override
  public void check(ASTFunction fun) {
    String typeName;
    // check parameter types
    if (fun.getParameters().isPresent()) {
      for (ASTParameter par : fun.getParameters().get().getParameters()) {
        typeName = Names.getQualifiedName(par.getType().getParts());

        Optional<? extends Scope> enclosingScope = fun.getEnclosingScope();
        Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + fun);
        Optional<NESTMLTypeSymbol> type = enclosingScope.get().resolve(typeName, NESTMLTypeSymbol.KIND);

        checkIfValidType(fun, typeName, type);

      }

      // check return type
      if (fun.getReturnType().isPresent()) {
        typeName = Names.getQualifiedName(fun.getReturnType().get().getParts());

        final Optional<? extends Scope> enclosingScope = fun.getEnclosingScope();
        Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + fun);
        final Optional<NESTMLTypeSymbol> type = enclosingScope.get().resolve(typeName, NESTMLTypeSymbol.KIND);
        checkIfValidType(fun, typeName, type);

        //doCheck(type.get(), fun.getReturnType().get(), true);
      }
    }

  }

  public void checkIfValidType(ASTNode decl, String typeName, Optional<NESTMLTypeSymbol> type) {
    if (!type.isPresent() || type.isPresent() && type.get().getName().endsWith("Logger")) {
      final String msgPredefined = "The type '%s' is a neuron/component. No neurons/components allowed " +
          "in this place. Use the use-statement.";
      CoCoLog.error(
          ERROR_CODE,
          String.format(msgPredefined, typeName),
          decl.get_SourcePositionStart());
    }
  }

  @Override
  public void check(ASTUSE_Stmt astUseStmt) {
    String typeName = Names.getQualifiedName(astUseStmt.getName().getParts());
    Optional<? extends Scope> enclosingScope = astUseStmt.getEnclosingScope();
    checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node at: " + astUseStmt.get_SourcePositionStart());
    Optional<NESTMLNeuronSymbol> type = enclosingScope.get().resolve(typeName, NESTMLNeuronSymbol.KIND);

    if (!type.isPresent()) {
      final String msgPredefined = "The type '%s' is a neuron/component. No neurons/components allowed " +
          "in this place. Use the use-statement.";
      CoCoLog.error(
          ERROR_CODE,
          String.format(msgPredefined, typeName),
          astUseStmt.get_SourcePositionStart());
    }

  }


}
