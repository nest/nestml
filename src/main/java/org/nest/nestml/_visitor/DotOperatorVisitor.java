package org.nest.nestml._visitor;

import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class DotOperatorVisitor implements NESTMLVisitor {

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> lhsTypeE = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsTypeE = expr.getRight().get().getType();

    if (lhsTypeE.isError()) {
      expr.setType(lhsTypeE);
      return;
    }
    if (rhsTypeE.isError()) {
      expr.setType(rhsTypeE);
      return;
    }

    TypeSymbol lhsType = lhsTypeE.getValue();
    TypeSymbol rhsType = rhsTypeE.getValue();

    if (expr.isModuloOp()) {
      if (isInteger(lhsType) && isInteger(rhsType)) {
        expr.setType(Either.value(getIntegerType()));
        return;
      }
      else {
        final String errorMsg = CommonsErrorStrings.messageModulo(this, expr.get_SourcePositionStart());
        expr.setType(Either.error(errorMsg));
        error(errorMsg, expr.get_SourcePositionStart());
        return;
      }
    }
    if (expr.isDivOp() || expr.isTimesOp()) {
      if (isNumeric(lhsType) && isNumeric(rhsType)) {

        // If both are units, calculate resulting Type
        if (lhsType.getType() == TypeSymbol.Type.UNIT
            && rhsType.getType() == TypeSymbol.Type.UNIT) {
          UnitRepresentation leftRep = UnitRepresentation.getBuilder().serialization(lhsType.getName()).build();
          UnitRepresentation rightRep = UnitRepresentation.getBuilder().serialization(rhsType.getName()).build();
          if (expr.isTimesOp()) {
            TypeSymbol returnType = getTypeIfExists((leftRep.multiplyBy(rightRep)).serialize())
                .get();//Register type on the fly
            expr.setType(Either.value(returnType));
            return;
          }
          else if (expr.isDivOp()) {
            TypeSymbol returnType = getTypeIfExists((leftRep.divideBy(rightRep)).serialize())
                .get();//Register type on the fly
            expr.setType(Either.value(returnType));
            return;
          }
        }
        //if lhs is Unit, and rhs real or integer, return same Unit
        if (lhsType.getType() == TypeSymbol.Type.UNIT) {
          expr.setType(Either.value(lhsType));
          return;
        }
        //if lhs is real or integer and rhs a unit, return unit for timesOP and inverse(unit) for divOp
        if (rhsType.getType() == TypeSymbol.Type.UNIT) {
          if (expr.isTimesOp()) {
            expr.setType(Either.value(rhsType));
            return;
          }
          else if (expr.isDivOp()) {
            UnitRepresentation rightRep = UnitRepresentation.getBuilder().serialization(rhsType.getName()).build();
            TypeSymbol returnType = getTypeIfExists((rightRep.invert()).serialize()).get();//Register type on the fly
            expr.setType(Either.value(returnType));
            return;
          }

        }
        //if no Units are involved, Real takes priority
        if (lhsType == getRealType() || rhsType == getRealType()) {
          expr.setType(Either.value(getRealType()));
          return;
        }

        // e.g. both are integers, but check to be sure
        if (lhsType == getIntegerType() || rhsType == getIntegerType()) {
          expr.setType(Either.value(getIntegerType()));
          return;
        }
      }
    }

    //Catch-all if no case has matched
    final String typeMissmatch = lhsType.prettyPrint() + (expr.isDivOp() ? " / " : " * ") + rhsType.prettyPrint();


    final String errorMsg = CommonsErrorStrings.messageType(this, typeMissmatch, expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
    error(errorMsg, expr.get_SourcePositionStart());
  }
}
