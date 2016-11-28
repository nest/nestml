package org.nest.commons._visitor;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class LineOperatorVisitor implements CommonsVisitor{
  final String ERROR_CODE = "NESTML_LINE_OPERATOR_VISITOR: ";

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
      //both are units
      if (lhsType.getValue().getType() == TypeSymbol.Type.UNIT &&
          rhsType.getValue().getType() == TypeSymbol.Type.UNIT) {
        if (isCompatible(lhsType.getValue(), rhsType.getValue())) {

          //TODO better solution
          //Make sure that ignoreMagnitude gets propagated if set
          if(rhsType.getValue().getName().substring(rhsType.getValue().getName().length()-1).equals("I")){
              expr.setType(rhsType);
          }else{
              expr.setType(lhsType);
          }
          // expr.setType(lhsType); //set either of the (same) unit types
          return;
        }
      }

      //at least one real
      if (lhsType.getValue() == getRealType() || rhsType.getValue() == getRealType()) {
        if(lhsType.getValue().getType()== TypeSymbol.Type.UNIT||
            rhsType.getValue().getType()== TypeSymbol.Type.UNIT){
          warn(ERROR_CODE+"Addition/substraction of unit and primitive type. Assuming real at "+expr.get_SourcePositionStart());
        }
        expr.setType(Either.value(getRealType()));
        return;
      }

      // e.g. at least one integer
      if (lhsType.getValue() == (getIntegerType()) || rhsType.getValue() == (getIntegerType())) {
        if(lhsType.getValue().getType()== TypeSymbol.Type.UNIT||
            rhsType.getValue().getType()== TypeSymbol.Type.UNIT){
          warn(ERROR_CODE+"Addition/substraction of unit and primitive type. Assuming real at "+expr.get_SourcePositionStart());
          //unit casts to real -> casts whole expression to real
          expr.setType(Either.value(getRealType()));
          return;
        }else{ //both integer
          expr.setType(Either.value(getIntegerType()));
          return;
        }
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
