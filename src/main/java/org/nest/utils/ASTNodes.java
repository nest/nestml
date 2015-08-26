/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import de.se_rwth.commons.Names;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLInheritanceVisitor;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.util.Collection;
import java.util.List;

/**
 * Helper class containing common operations concerning ASTNodes
 * 
 * @author Sebastian Oberhoff
 */
public final class ASTNodes {
  
  private ASTNodes() {
    // noninstantiable
  }

  public static List<String> getVariablesNamesFromAst(final ASTSPLNode astNode) {
    final FQNCollector fqnCollector = new FQNCollector();
    astNode.accept(fqnCollector);
    return fqnCollector.getVariableNames();
  }

  private final static class SPLNodesCollector implements SPLInheritanceVisitor {

    private List<ASTReturnStmt> returnStmts = Lists.newArrayList();

    public void startVisitor(ASTBlock blockAst) {
      blockAst.accept(this);
    }

    @Override
    public void visit(ASTReturnStmt astReturnStmt) {
      returnStmts.add(astReturnStmt);
    }

    public List<ASTReturnStmt> getReturnStmts() {
      return returnStmts;
    }
  }

  public static List<ASTReturnStmt> getReturnStatements(ASTBlock blockAst) {
    final SPLNodesCollector splNodesCollector = new SPLNodesCollector();
    splNodesCollector.startVisitor(blockAst);
    return splNodesCollector.getReturnStmts();
  }

  static final class FQNCollector implements NESTMLInheritanceVisitor {
    public List<String> getVariableNames() {
      return variableNames;
    }

    final private List<String> variableNames = Lists.newArrayList();

    @Override
    public void visit(final ASTExpr astExpr) {
      if (astExpr.getQualifiedName().isPresent()) {
        final String variableName = Names.getQualifiedName(astExpr.getQualifiedName().get().getParts());
        variableNames.add(variableName);

      }

    }

  }

  public static List<String> getArgumentsTypes(
      final ASTFunctionCall astFunctionCall,
      final PredefinedTypesFactory typesFactory) {
    final List<String> argTypeNames = Lists.newArrayList();

    final ExpressionTypeCalculator typeCalculator =  new ExpressionTypeCalculator(typesFactory);

    for (int i = 0; i < astFunctionCall.getArgList().getArgs().size(); ++i) {
      final ASTExpr arg = astFunctionCall.getArgList().getArgs().get(i);
      final NESTMLTypeSymbol argType = typeCalculator.computeType(arg);
      argTypeNames.add(argType.getName());
    }

    return argTypeNames;
  }

}
