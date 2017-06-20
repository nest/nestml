package org.nest.nestml._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._cocos.SplErrorStrings;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.*;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class LineOperatorVisitor implements NESTMLVisitor {

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

    //Plus-exclusive code
    if (expr.isPlusOp()) {
      // String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string

      if ((lhsType == (getStringType()) ||
           rhsType == (getStringType())) &&
          (rhsType != (getVoidType()) && lhsType != (getVoidType()))) {
        expr.setType(Either.value(getStringType()));
        return;
      }
    }

    //Common code for plus and minus ops:
    if (isNumeric(lhsType) && isNumeric(rhsType)) {
      //both match exactly -> any is valid, in case of units propagate IgnoreMagnitude
      if (lhsType.prettyPrint().equals(rhsType.prettyPrint())) {
        //Make sure that ignoreMagnitude gets propagated if set
        if (isUnit(rhsType)) {
          UnitRepresentation rhsRep = UnitRepresentation.getBuilder().serialization(rhsType.getName()).build();
          if (rhsRep.isIgnoreMagnitude()) {
            expr.setType(Either.value(rhsType));
          }
          else {
            expr.setType(Either.value(lhsType));
          }
        }
        else {
          expr.setType(Either.value(lhsType)); //no units involved, any is valid
        }
        return;
      }
      //both numeric primitive, not matching -> 1 real one integer -> real
      if (isNumericPrimitive(lhsType) && isNumericPrimitive(rhsType)) {
        expr.setType(Either.value(getRealType()));
        return;
      }
      //Both are units, not matching -> see if matching base
      if(isUnit(lhsType)&&isUnit(rhsType)){
        //Base not matching -> error
        UnitRepresentation rhsRep = UnitRepresentation.getBuilder().serialization(rhsType.getName()).build();
        UnitRepresentation lhsRep = UnitRepresentation.getBuilder().serialization(lhsType.getName()).build();
        if(!lhsRep.equalBase(rhsRep)) {
          final String errorMsg = CommonsErrorStrings.messageDifferentTypes(
              this,
              lhsType.prettyPrint(),
              rhsType.prettyPrint(),
              "real",
              expr.get_SourcePositionStart());
          expr.setType(Either.value(getRealType()));
          warn(errorMsg, expr.get_SourcePositionStart());
          return;
        }else{//Base matching, install conversion

          //Determine the difference in magnitude
          int magDiff = lhsRep.getMagnitude() - rhsRep.getMagnitude();

          //replace left expression with multiplication
          expr.setLeft(AstUtils.createSubstitution(expr.getLeft().get(),magDiff));

          //revisit current sub-tree with substitution
          ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
          expr.accept(expressionTypeVisitor);

          //drop warning about implicit conversion
          final String warnMsg = SplErrorStrings.messageImplicitConversion(
              this,
              lhsType.prettyPrint(),
              rhsType.prettyPrint(),
              expr.get_SourcePositionStart());
          Log.warn(warnMsg,expr.get_SourcePositionStart());

          return;

        }
      }
      //one is unit and one numeric primitive and vice versa -> assume unit, warn
      if ((isUnit(lhsType) && isNumericPrimitive(rhsType)) ||
          (isUnit(rhsType) && isNumericPrimitive(lhsType))) {
        TypeSymbol unitType;
        if (isUnit(lhsType)) {
          unitType = lhsType;
        }
        else {
          unitType = rhsType;
        }

        final String errorMsg = CommonsErrorStrings.messageDifferentTypes(
            this,
            lhsType.prettyPrint(),
            rhsType.prettyPrint(),
            unitType.prettyPrint(),
            expr.get_SourcePositionStart());
        expr.setType(Either.value(unitType));
        warn(errorMsg, expr.get_SourcePositionStart());
        return;
      }
    }

    //If a buffer is involved, the other unit takes precedent TODO: is this the intended semantic?
    if (lhsType == getBufferType()) {
      expr.setType(Either.value(rhsType));
      return;
    }
    if (rhsType == getBufferType()) {
      expr.setType(Either.value(lhsType));
      return;
    }

    //if we get here, we are in a general error state
    final String errorMsg = CommonsErrorStrings.messageTypeError(
        this,
        lhsType.prettyPrint(),
        rhsType.prettyPrint(),
        expr.isPlusOp() ? "addition" : "substraction",
        expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
    error(errorMsg, expr.get_SourcePositionStart());
  }

}
