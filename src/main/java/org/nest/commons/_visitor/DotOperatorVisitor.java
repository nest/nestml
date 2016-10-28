package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.commons._visitor.ExpressionTypeVisitor.isNumeric;
import static org.nest.symboltable.predefined.PredefinedTypes.*;
/**
 * @author ptraeder
 */
public class DotOperatorVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    checkState(expr.getLeft().get().getType().isPresent());
    checkState(expr.getRight().get().getType().isPresent());
    final Either<TypeSymbol, String> lhsType = expr.getLeft().get().getType().get();
    final Either<TypeSymbol, String> rhsType = expr.getRight().get().getType().get();

    if (lhsType.isError()) {
      expr.setType(lhsType);
      return;
    }
    if (rhsType.isError()) {
      expr.setType(rhsType);
      return;
    }

    //TODO: modulo semantics
    if(expr.isDivOp() || expr.isTimesOp()) {
      if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue())) {

        // If both are units, calculate resulting Type
        if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT
            && rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          UnitRepresentation leftRep = new UnitRepresentation(lhsType.getValue().getName());
          UnitRepresentation rightRep = new UnitRepresentation(rhsType.getValue().getName());
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
        if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          expr.setType(Either.value(lhsType.getValue()));
          return;
        }
        //if lhs is real or integer and rhs a unit, return unit for timesOP and inverse(unit) for divOp
        if (rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
          if (expr.isTimesOp()) {
            expr.setType(Either.value(rhsType.getValue()));
            return;
          }
          else if (expr.isDivOp()) {
            UnitRepresentation rightRep = new UnitRepresentation(rhsType.getValue().getName());
            TypeSymbol returnType = getTypeIfExists((rightRep.invert()).serialize()).get();//Register type on the fly
            expr.setType(Either.value(returnType));
            return;
          }

        }
        //if no Units are involved, Real takes priority
        if (lhsType.getValue() == getRealType() || rhsType.getValue() == getRealType()) {
          expr.setType(Either.value(getRealType()));
          return;
        }

        // e.g. both are integers, but check to be sure
        if (lhsType.getValue() == getIntegerType() || rhsType.getValue() == getIntegerType()) {
          expr.setType(Either.value(getIntegerType()));
          return;
        }
      }
      //If a buffer is involved, the other unit takes precedent TODO: is this the intended semantic?
      if(lhsType.getValue() == getBufferType()){
        expr.setType(Either.value(rhsType.getValue()));
        return;
      }
      if(rhsType.getValue() == getBufferType()){
        expr.setType(Either.value(lhsType.getValue()));
        return;
      }
    }

    //Catch-all if no case has matched
    String msg = "Cannot determine the type of the expression: " + AstUtils.toString(expr);
    expr.setType(Either.error(msg));

  }
}
