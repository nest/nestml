package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitTranslator;

import java.util.Optional;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class NumericLiteralVisitor implements CommonsVisitor{
  UnitTranslator unitTranslator = new UnitTranslator();
  @Override
  public void visit(ASTExpr expr) {
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
