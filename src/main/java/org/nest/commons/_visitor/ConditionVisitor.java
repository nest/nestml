package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumericPrimitive;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isReal;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 *  @author ptraeder
 * */
public class ConditionVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_CONDITION_VISITOR: ";

  @Override
  public void visit(ASTExpr expr) {
    if (expr.getCondition().isPresent()) {
      final Either<TypeSymbol, String> condition = expr.getCondition().get().getType();
      final Either<TypeSymbol, String> ifTrue = expr.getIfTrue().get().getType();
      final Either<TypeSymbol, String> ifNot = expr.getIfNot().get().getType();

      if (condition.isError()) {
        expr.setType(condition);
        return;
      }
      if (ifTrue.isError()) {
        expr.setType(ifTrue);
        return;
      }
      if (ifNot.isError()) {
        expr.setType(ifNot);
        return;
      }

      if (!condition.getValue().equals(getBooleanType())) {
        final String errorMsg = ERROR_CODE+"The ternary operator condition must be boolean.";
        expr.setType(Either.error(errorMsg));
        Log.error(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //Alternatives match exactly -> any is valid
      if(ifTrue.getValue().equals(ifNot.getValue())){
        expr.setType(ifTrue);
        return;
      }

      //Both are units -> real
      if(isUnit(ifTrue.getValue())&&isUnit(ifNot.getValue())){
        final String errorMsg = ERROR_CODE+
            "Mismatched conditional alternatives "+ifTrue.getValue().prettyPrint()+" and "+
                ifNot.getValue().prettyPrint()+"-> Assuming real";
        expr.setType(Either.value(getRealType()));
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //one Unit and one numeric primitive and vice versa -> assume unit,warn
      if((isUnit(ifTrue.getValue())&&isNumericPrimitive(ifNot.getValue()))||
          isUnit(ifNot.getValue())&&isNumericPrimitive(ifTrue.getValue())){
        final String errorMsg = ERROR_CODE+
            "Mismatched conditional alternatives "+ifTrue.getValue().prettyPrint()+" and "+
                ifNot.getValue().prettyPrint()+"-> Assuming real";
        TypeSymbol unitType;
        if(isUnit(ifTrue.getValue())){
          unitType = ifTrue.getValue();
        }else{
          unitType = ifNot.getValue();
        }
        expr.setType(Either.value(unitType));
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }

      //both are numeric primitives (and not equal) ergo one is real and one is integer -> real
      if(isNumericPrimitive(ifTrue.getValue())&&isNumericPrimitive(ifNot.getValue())){
        expr.setType(Either.value(getRealType()));
        return;
      }

      //if we get here it is an error
      final String errorMsg = ERROR_CODE+
          "Mismatched conditional alternatives "+ifTrue.getValue().prettyPrint()+" and "+
          ifNot.getValue().prettyPrint()+".";
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg,expr.get_SourcePositionStart());
      return;
    }
  }
}
