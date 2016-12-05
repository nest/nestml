package org.nest.commons._visitor;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumericPrimitive;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class LineOperatorVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_LINE_OPERATOR_VISITOR: ";

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> lhsType = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsType = expr.getRight().get().getType();


    if (lhsType.isError()) {
      expr.setType(lhsType);
      return;
    }
    if (rhsType.isError()) {
      expr.setType(rhsType);
      return;
    }

    //Format error string..

    //Plus-exclusive code
    if (expr.isPlusOp()) {
      // String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string

      if ((lhsType.getValue() == (getStringType()) ||
          rhsType.getValue() == (getStringType())) &&
          (rhsType.getValue() != (getVoidType()) && lhsType.getValue() != (getVoidType()))) {
        expr.setType(Either.value(getStringType()));
        return;
      }
    }

    //Common code for plus and minus ops:
    if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue())) {
      //both match exactly -> any is valid, in case of units propagate IgnoreMagnitude
      if (lhsType.getValue().equals(rhsType.getValue())) {
          //Make sure that ignoreMagnitude gets propagated if set
          if(isUnit(rhsType.getValue())){
            UnitRepresentation rhsRep = new UnitRepresentation(rhsType.getValue().getName());
            if(rhsRep.isIgnoreMagnitude()){
              expr.setType(rhsType);
            }else{
              expr.setType(lhsType);
            }
          }else{
            expr.setType(lhsType); //no units involved, any is valid
          }
          return;
      }
      //both numeric primitive, not matching -> 1 real one integer -> real
      if (isNumericPrimitive(lhsType.getValue())&&isNumericPrimitive(rhsType.getValue())) {
        expr.setType(Either.value(getRealType()));
        return;
      }
      //Both are units, not matching -> real, warn
      if(isUnit(lhsType.getValue())&&isUnit(rhsType.getValue())){
        final String errorMsg =ERROR_CODE+
            "Addition/substraction of "+lhsType.getValue().prettyPrint()+" and "+rhsType.getValue().prettyPrint()+
            ". Assuming real.";
        expr.setType(Either.value(getRealType()));
        warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //one is unit and one real/integer and vice versa -> assume unit and warn
      if(isUnit(lhsType.getValue())&&isNumericPrimitive(rhsType.getValue())){
        final String errorMsg =ERROR_CODE+
            "Addition/substraction of "+lhsType.getValue().prettyPrint()+" and "+rhsType.getValue().prettyPrint()+
            ". Assuming "+lhsType.getValue().prettyPrint();
        expr.setType(lhsType);
        warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      if(isUnit(rhsType.getValue())&&isNumericPrimitive(lhsType.getValue())){
        final String errorMsg =ERROR_CODE+
            "Addition/substraction of "+lhsType.getValue().prettyPrint()+" and "+rhsType.getValue().prettyPrint()+
            ". Assuming "+rhsType.getValue().prettyPrint();
        expr.setType(rhsType);
        warn(errorMsg,expr.get_SourcePositionStart());
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

    //if we get here, we are in a general error state
    final String errorMsg = ERROR_CODE+"Cannot determine the type of "+ (expr.isPlusOp()?"addition":"substraction")+" with types: " +
        lhsType.getValue().prettyPrint()+ " and " + rhsType.getValue().prettyPrint();
    expr.setType(Either.error(errorMsg));
    error(errorMsg,expr.get_SourcePositionStart());
    return;
  }
}
