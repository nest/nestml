package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units._ast.ASTUnitType;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.units.unitrepresentation.UnitTranslator;

import java.util.Optional;

import static org.nest.spl.symboltable.typechecking.TypeChecker.checkUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class NESTMLNumericLiteralVisitor implements CommonsVisitor{
  UnitTranslator unitTranslator = new UnitTranslator();
  @Override
  public void visit(ASTExpr expr) {
    Optional<TypeSymbol> exprType = Optional.empty();

    if (expr.getNESTMLNumericLiteral().get().getType().isPresent()) {
      String unitName = expr.getNESTMLNumericLiteral().get().getType().get().getSerializedUnit(); //guaranteed after successful NESTML Parser run
      exprType = getTypeIfExists(unitName);

    }

    if (exprType.isPresent() && checkUnit(exprType.get())) { //Try Unit Type
      expr.setType(Either.value(exprType.get()));
      return;
    }

    else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTDoubleLiteral) {
      expr.setType(Either.value(getRealType()));
      return;
    }
    else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
      expr.setType(Either.value(getIntegerType()));
      return;
    }
  }
}
