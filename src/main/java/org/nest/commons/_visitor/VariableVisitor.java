package org.nest.commons._visitor;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

/**
 * @author ptraeder
 */
public class VariableVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    final Scope scope = expr.getEnclosingScope().get();
    final String varName = expr.getVariable().get().toString();
    final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

    if (var.isPresent()) {
      expr.setType(Either.value(var.get().getType()));
    }
    else {
      expr.setType(Either.error("ExpressionCalculator cannot resolve the type of the variable: " + varName));
    }
  }
}
