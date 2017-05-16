package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTDoubleLiteral;
import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Optional;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class NESTMLNumericLiteralVisitor implements CommonsVisitor {

  @Override
  public void visit(ASTExpr expr) {
    Optional<TypeSymbol> exprType = Optional.empty();

    if (expr.getNESTMLNumericLiteral().get().getType().isPresent()) {
      String unitName = expr.getNESTMLNumericLiteral().get().getType().get().getSerializedUnit(); //guaranteed after successful NESTML Parser run
      exprType = getTypeIfExists(unitName);

    }

    if (exprType.isPresent() && isUnit(exprType.get())) { //Try Unit Type
      expr.setType(Either.value(exprType.get()));
    }
    else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTDoubleLiteral) {
      expr.setType(Either.value(getRealType()));
    }
    else if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
      expr.setType(Either.value(getIntegerType()));
    }

  }

}
