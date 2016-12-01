package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumericPrimitive;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isReal;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 *  @author ptraeder
 * */
public class ConditionVisitor implements CommonsVisitor{
  final String ERROR_CODE = "NESTML_CONDITION_VISITOR: ";

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

      //Both are units -> tie break by using the first
      if(isUnit(ifTrue.getValue())&&isUnit(ifNot.getValue())){
        final String errorMsg = ERROR_CODE+
            "Mismatched conditional alternatives "+ifTrue.getValue().prettyPrint()+" and "+
                ifNot.getValue().prettyPrint()+"-> Assuming "+ifTrue.getValue().prettyPrint();
        expr.setType(ifTrue);
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //integer and real -> real
      if(isNumericPrimitive(ifTrue.getValue())&&isNumericPrimitive(ifNot.getValue())){
        final String errorMsg = ERROR_CODE+
            "Mismatched numeric primitives in conditional alternatives -> Assuming real";
        expr.setType(Either.value(getRealType()));
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //one Unit and one primitive and vice versa -> return unit
      if(isUnit(ifTrue.getValue())&&isNumericPrimitive(ifNot.getValue())){
        final String errorMsg = ERROR_CODE+
            "Mismatched conditional alternatives "+ifTrue.getValue().prettyPrint()+" and "+
                ifNot.getValue().prettyPrint()+"-> Assuming "+ifTrue.getValue().prettyPrint();
        expr.setType(ifTrue);
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      if(isUnit(ifNot.getValue())&&isNumericPrimitive(ifTrue.getValue())){
        final String errorMsg = ERROR_CODE+
            "Mismatched conditional alternatives "+ifTrue.getValue().prettyPrint()+" and "+
                ifNot.getValue().prettyPrint()+ "-> Assuming "+ifNot.getValue().prettyPrint();
        expr.setType(ifNot);
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
    }
  }
}
