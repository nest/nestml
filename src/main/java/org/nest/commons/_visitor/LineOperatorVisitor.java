package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.commons._visitor.ExpressionTypeVisitor.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class LineOperatorVisitor implements CommonsVisitor{

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

    //Format error string..
    String rhsPrettyType,lhsPrettyType;
    if(rhsType.getValue().getType() == TypeSymbol.Type.UNIT){
      rhsPrettyType  = new UnitRepresentation(rhsType.getValue().getName()).prettyPrint();
    }else{
      rhsPrettyType = rhsType.getValue().getName();
    }
    if(lhsType.getValue().getType() == TypeSymbol.Type.UNIT){
      lhsPrettyType  = new UnitRepresentation(lhsType.getValue().getName()).prettyPrint();
    }else{
      lhsPrettyType = lhsType.getValue().getName();
    }
    final String errorMsg = "Cannot determine the type of the "+ (expr.isPlusOp()?"(plus)":"(minus)")+" operation with types: " + lhsPrettyType
        + " and " + rhsPrettyType + " at " + expr.get_SourcePositionStart() + ">";

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
      // in this case, neither of the sides is a String
      //both are units
      if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT &&
          rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
        if (isCompatible(lhsType.getValue(), rhsType.getValue())) {
          expr.setType(lhsType); //set either of the (same) unit types
          return;
        }
      }
      // in this case, neither of the sides is a String
      if (lhsType.getValue() == getRealType() || rhsType.getValue() == getRealType()) {
        expr.setType(Either.value(getRealType()));
        return;
      }

      // e.g. both are integers, but check to be sure
      if (lhsType.getValue() == (getIntegerType()) || rhsType.getValue() == (getIntegerType())) {
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

    //if we get here, we are in an error state
    expr.setType(Either.error(errorMsg));
    return;
  }
}
