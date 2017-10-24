package org.nest.nestml._visitor;

import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.getRealType;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.getType;

/**
 * @author ptraeder
 */
public class VariableVisitor implements NESTMLVisitor {

  @Override
  public void visit(final ASTExpr expr) {
    checkArgument(expr.getEnclosingScope().isPresent(), "Run symboltable creator.");

    final String varName = expr.getVariable().get().toString();
    VariableSymbol var = VariableSymbol.resolve(varName, expr.getEnclosingScope().get());

    expr.setType(Either.value(var.getType()));

  }

}
