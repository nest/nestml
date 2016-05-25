package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTVariable;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.utils.ASTNodes;

import java.io.IOException;
import java.io.StringReader;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static com.google.common.collect.Lists.newArrayList;

/**
 * Folds an expression if it depends only on non-state variables, which cannot evolve during the simulation run.
 * E.g. "y1_I_shape_in*exp(-h/tau_syn_in)" can be decomposted into a "y1_I_shape_in*tmp" and an internal variable
 * tmp real = exp(-h/tau_syn_in).
 * @author plotnikov
 */
class ExpressionFolder {
  private static final NESTMLParser parser = new NESTMLParser();

  private final List<ASTExpr> nodesToReplace = newArrayList();
  private final List<String> internalVariables = newArrayList();

  public List<ASTExpr> getNodesToReplace() {
    return nodesToReplace;
  }

  public List<String> getInternalVariables() {
    return internalVariables;
  }

  public void fold(
      final ASTExpr expr,
      final List<String> stateVariableNames,
      final String variablePrefix) {
    try {
      final ExpressionVisitor expressionVisitor = new ExpressionVisitor(stateVariableNames);
      expr.accept(expressionVisitor);

      for (int i = 0; i < expressionVisitor.getNodesToReplace().size(); ++i) {
        final ASTExpr child = expressionVisitor.getNodesToReplace().get(0);
        final Optional<ASTNode> parent = ASTNodes.getParent(child, expr);
        checkState(parent.isPresent(), "Should not happen by construction.");
        checkState(parent.get() instanceof ASTExpr, "Should not happen by construction.");

        final ASTExpr parentExpr = (ASTExpr) parent.get();
        final String tmpVariable = variablePrefix + 1;
        internalVariables.add(tmpVariable);
        final Optional<ASTExpr> replacementVariable = parser.parseExpr(new StringReader(tmpVariable));
        if (parentExpr.getLeft().isPresent() && parentExpr.getLeft().get().equals(child)) {
          parentExpr.setLeft(replacementVariable.get());
        }
        if (parentExpr.getRight().isPresent() && parentExpr.getRight().get().equals(child)) {
          parentExpr.setRight(replacementVariable.get());
        }
      }

    } catch (IOException e) {
      throw new RuntimeException("Should not happen by construction.", e);
    }

  }

  private class ExpressionVisitor implements NESTMLInheritanceVisitor {
    final List<String> stateVariableNames;

    private ExpressionVisitor(final List<String> stateVariableNames) {
      this.stateVariableNames = stateVariableNames;
    }
    private List<ASTExpr> getNodesToReplace() {
      return nodesToReplace;
    }

    @Override
    public void visit(final ASTExpr expr) {

      final Optional<ASTVariable> stateVariable = ASTNodes.getAll(expr, ASTVariable.class)
          .stream()
          .filter(astVariable -> stateVariableNames.contains(astVariable.toString()))
          .findAny();

      boolean canBeFolded = !stateVariable.isPresent() && ASTNodes.getAll(expr, ASTVariable.class).size() > 1;

      if (canBeFolded) {
        addCandidate(expr);
      }

    }

    private void addCandidate(final ASTExpr expr) {
      final Optional<ASTExpr> result = nodesToReplace.stream().filter(parent -> isParentOf(parent, expr)).findAny();
      if (!result.isPresent()) {
        nodesToReplace.add(expr);
      }

    }

    private boolean isParentOf(final ASTNode parent, final ASTNode child) {
      return ASTNodes.getSuccessors(parent).contains(child);
    }
  }



}