/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import com.google.common.collect.Queues;
import com.google.common.collect.Sets;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.Util;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLInheritanceVisitor;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Deque;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Helper class containing common operations concerning ast nodes.
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

  /**
   * Finds the first node of the required type
   * @param root The root node from where the search starts
   * @param clazz The required type
   * @return The fist node of the required type or empty value.
   */
  public static <T> Optional<T> getAny(ASTNode root, Class<T> clazz) {
    final Iterable<ASTNode> nodes = Util.preOrder(root, ASTNode::get_Children);

    for (ASTNode node:nodes) {
      if (clazz.isInstance(node)) {
        // it is checked by the if-conditions. only T types are handled
        return Optional.of((T) node);
      }
    }

    return Optional.empty();
  }

  /**
   * Finds the first node of the required type
   * @param root The root node from where the search starts
   * @param clazz The required type
   * @return The list with all nodes of the required type.
   */
  public static <T> List<T> getAll(ASTNode root, Class<T> clazz) {
    final Iterable<ASTNode> nodes = Util.preOrder(root, ASTNode::get_Children);
    final List<T> resultList = Lists.newArrayList();
    for (ASTNode node:nodes) {
      if (clazz.isInstance(node)) {
        // it is checked by the if-conditions. only T types are handled
        resultList.add((T) node);
      }
    }

    return resultList;
  }

  /**
   * Returns all variables defined in the tree starting from the astNode.
   */
  public static List<String> getVariablesNamesFromAst(final ASTSPLNode astNode) {
    final FQNCollector fqnCollector = new FQNCollector();
    astNode.accept(fqnCollector);
    return fqnCollector.getVariableNames();
  }

  public static List<ASTReturnStmt> getReturnStatements(ASTBlock blockAst) {
    final SPLNodesCollector splNodesCollector = new SPLNodesCollector();
    splNodesCollector.startVisitor(blockAst);
    return splNodesCollector.getReturnStmts();
  }

  public static List<String> getArgumentsTypes(final ASTFunctionCall astFunctionCall) {
    final List<String> argTypeNames = Lists.newArrayList();

    final ExpressionTypeCalculator typeCalculator =  new ExpressionTypeCalculator();

    for (int i = 0; i < astFunctionCall.getArgList().getArgs().size(); ++i) {
      final ASTExpr argExpr = astFunctionCall.getArgList().getArgs().get(i);
      final Either<TypeSymbol, String> argType = typeCalculator.computeType(argExpr);
      if (argType.isLeft()) {
        argTypeNames.add(argType.getLeft().get().getName());
      }
      else {
        // TODO print the value of the expression
        throw new RuntimeException("Cannot determine the type of the expression");
      }

    }

    return argTypeNames;
  }

  public static String toString(final ASTQualifiedName qualifiedName) {
    return Names.getQualifiedName(qualifiedName.getParts());
  }

  public static String toString(final ASTExpr expr) {
    final ExpressionsPrettyPrinter printer = new ExpressionsPrettyPrinter();
    return printer.print(expr);
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

  static final class FQNCollector implements NESTMLInheritanceVisitor {
    public List<String> getVariableNames() {
      return Lists.newArrayList(variableNames);
    }

    final private Set<String> variableNames = Sets.newHashSet();

    @Override
    public void visit(final ASTExpr astExpr) {
      if (astExpr.getQualifiedName().isPresent()) {
        final String variableName = Names.getQualifiedName(astExpr.getQualifiedName().get().getParts());
        variableNames.add(variableName);

      }

    }

  }

  /**
   * Returns all variable symbols for variables which are defined in the subtree starting from
   * the astNode.
   */
  public static List<VariableSymbol> getVariableSymbols(final ASTNESTMLNode astNode) {
    final DeclarationsCollector variableSymbolsCollector = new DeclarationsCollector();
    astNode.accept(variableSymbolsCollector);
    return variableSymbolsCollector.getVariableSymbols();
  }

  static final class DeclarationsCollector implements NESTMLInheritanceVisitor {
    public List<VariableSymbol> getVariableSymbols() {
      return Lists.newArrayList(variables);
    }

    final private Set<VariableSymbol> variables = Sets.newHashSet();

    @Override
    public void visit(final ASTDeclaration astDeclaration) {
      checkArgument(astDeclaration.getEnclosingScope().isPresent(), "Run symbol table creator.");
      final Scope scope = astDeclaration.getEnclosingScope().get();
      for (final String variableName:astDeclaration.getVars()) {
        final Optional<VariableSymbol> symbol = scope.resolve(variableName, VariableSymbol.KIND);
        if (symbol.isPresent()) {
          variables.add(symbol.get());
        }
        else {
          Log.warn("Cannot resolve the variable: " + variableName);
        }
      }

    }

  }
  /**
   * Returns all variable symbols for variables which are defined in the subtree starting from
   * the astNode.
   */
  public static List<VariableSymbol> getVariableSymbols(final ASTSPLNode astNode) {
    final VariableSymbolsCollector variableSymbolsCollector = new VariableSymbolsCollector();
    astNode.accept(variableSymbolsCollector);
    return variableSymbolsCollector.getVariableSymbol();
  }

  static final class VariableSymbolsCollector implements NESTMLInheritanceVisitor {
    public List<VariableSymbol> getVariableSymbol() {
      return Lists.newArrayList(variables);
    }

    final private Set<VariableSymbol> variables = Sets.newHashSet();

    @Override
    public void visit(final ASTQualifiedName astQualifiedName) {
      checkArgument(astQualifiedName.getEnclosingScope().isPresent(), "Run symbol table creator.");
      final String variableName = ASTNodes.toString(astQualifiedName);
      final Scope scope = astQualifiedName.getEnclosingScope().get();
      final Optional<VariableSymbol> symbol = scope.resolve(variableName, VariableSymbol.KIND);
      if (symbol.isPresent()) {
        variables.add(symbol.get());
      }

    }

  }

  public static boolean isInvertableExpression(final ASTExpr astExpr) {
    // todo: check user defined functions
    // check: comparison and relational operations
    return true;
  }

}
