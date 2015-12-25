/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import com.google.common.collect.Queues;
import de.monticore.ast.ASTNode;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.Util;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLInheritanceVisitor;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Deque;
import java.util.List;
import java.util.Optional;

/**
 * Helper class containing common operations concerning ASTNodes
 * 
 * @author plotnikov, oberhoff
 */
public final class ASTNodes {
  
  private ASTNodes() {
    // noninstantiable
  }

  /**
   * Returns the unambiguous parent of the {@code queryNode}. Uses an breadthfirst traverse approach to collect nodes in the right order
   * @param queryNode The node direct parent of the given node
   * @param root The node that is an ancestor of the {@code queryNode}
   *
   * @return Parent of the queryNode or an Absent value if the parent was not found
   */
  public static Optional<ASTNode> getParent(ASTNode queryNode, ASTNode root) {

    final Deque<ASTNode> successors = Queues.newArrayDeque();

    final Iterable<ASTNode> tmp = Util.preOrder(root, ASTNode::get_Children);

    successors.add(root);
    for (ASTNode parentCandidate:tmp) {
      if (parentCandidate.get_Children().contains(queryNode)) {
        return Optional.of(parentCandidate);
      }
    }

    return Optional.empty();
  }


  public static <T> Optional<T> getAny(ASTNode root, Class<T> clazz) {
    final Iterable<ASTNode> nodes = Util.preOrder(root, ASTNode::get_Children);

    for (ASTNode node:nodes) {
      if (clazz.isInstance(node)) {
        // it is checked by the if-conditions

        return Optional.of((T) node);
      }
    }

    return Optional.empty();
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
      final TypeSymbol argType = typeCalculator.computeType(arg);
      argTypeNames.add(argType.getName());
    }

    return argTypeNames;
  }

  public static String toString(final ASTQualifiedName qualifiedName) {
    return Names.getQualifiedName(qualifiedName.getParts());
  }

}
