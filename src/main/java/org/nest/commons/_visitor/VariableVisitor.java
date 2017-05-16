package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;

/**
 * @author ptraeder
 */
public class VariableVisitor implements CommonsVisitor {

  @Override
  public void visit(final ASTExpr expr) {
    checkArgument(expr.getEnclosingScope().isPresent(), "Run symboltable creator.");

    final String varName = expr.getVariable().get().toString();
    VariableSymbol var = VariableSymbol.resolve(varName, expr.getEnclosingScope().get());

    if (var.isCurrentBuffer()) {
      expr.setType(Either.value(getType("pA")));
    }
    else if (var.isSpikeBuffer()) {
      expr.setType(Either.value(getRealType()));
    }
    else {
      expr.setType(Either.value(var.getType()));
    }
  }

}
