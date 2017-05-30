package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.UnitTranslator;

import java.util.Optional;

import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class NumericLiteralVisitor implements CommonsVisitor{
  UnitTranslator unitTranslator = new UnitTranslator();
  @Override
  public void visit(ASTExpr expr) {
    //if variable is also set in this expression, the var type overrides the literal
    if(expr.getVariable().isPresent()){
      final Scope scope = expr.getEnclosingScope().get();
      final String varName = expr.getVariable().get().toString();
      final Optional<VariableSymbol> variableSymbol = scope.resolve(varName, VariableSymbol.KIND);
      expr.setType(Either.value(variableSymbol.get().getType()));
      return;
    }

    if (expr.getNumericLiteral().get() instanceof ASTDoubleLiteral) {
      expr.setType(Either.value(getRealType()));
      return;
    }
    else if (expr.getNumericLiteral().get() instanceof ASTIntLiteral) {
      expr.setType(Either.value(getIntegerType()));
      return;
    }
  }
}
