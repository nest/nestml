package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumericPrimitive;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 *  @author ptraeder
 * */
public class ConditionVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_CONDITION_VISITOR";

  @Override
  public void visit(ASTExpr expr) {
    if (expr.getCondition().isPresent()) {
      final Either<TypeSymbol, String> condition = expr.getCondition().get().getType();
      final Either<TypeSymbol, String> ifTrueE = expr.getIfTrue().get().getType();
      final Either<TypeSymbol, String> ifNotE = expr.getIfNot().get().getType();

      if (condition.isError()) {
        expr.setType(condition);
        return;
      }
      if (ifTrueE.isError()) {
        expr.setType(ifTrueE);
        return;
      }
      if (ifNotE.isError()) {
        expr.setType(ifNotE);
        return;
      }

      TypeSymbol ifTrue = ifTrueE.getValue();
      TypeSymbol ifNot = ifNotE.getValue();

      if (!condition.getValue().equals(getBooleanType())) {
        final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +"The ternary operator condition must be boolean.";
        expr.setType(Either.error(errorMsg));
        Log.error(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //Alternatives match exactly -> any is valid
      if(ifTrue.prettyPrint().equals(ifNot.prettyPrint())){
        expr.setType(Either.value(ifTrue));
        return;
      }

      //Both are units -> try to recover, otherwise real
      if(isUnit(ifTrue)&&isUnit(ifNot)){
        UnitRepresentation ifNotRep = UnitRepresentation.getBuilder().serialization(ifTrue.getName()).build();
        UnitRepresentation ifTrueRep = UnitRepresentation.getBuilder().serialization(ifNot.getName()).build();
        if(ifTrueRep.equalBase(ifNotRep)) { //matching base, recover
          //Determine the difference in magnitude
          int magDiff = ifNotRep.getMagnitude() - ifTrueRep.getMagnitude();

          //replace left expression with multiplication
          expr.setIfTrue(AstUtils.createSubstitution(expr.getIfTrue().get(),magDiff));

          //revisit current sub-tree with substitution
          ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
          expr.accept(expressionTypeVisitor);

          //drop warning about implicit conversion
          Log.warn(ERROR_CODE +" "+AstUtils.print(expr.get_SourcePositionStart()) + " : Implicit conversion from "+ifTrueRep.prettyPrint()+" to "+ifNotRep.prettyPrint());
          return;
        }


        final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
            "Mismatched conditional alternatives "+ifTrue.prettyPrint()+" and "+
                ifNot.prettyPrint()+"-> Assuming real";
        expr.setType(Either.value(getRealType()));
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
      //one Unit and one numeric primitive and vice versa -> assume unit,warn
      if((isUnit(ifTrue)&&isNumericPrimitive(ifNot))||
          isUnit(ifNot)&&isNumericPrimitive(ifTrue)){
        TypeSymbol unitType;
        if(isUnit(ifTrue)){
          unitType = ifTrue;
        }else{
          unitType = ifNot;
        }
        final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
            "Mismatched conditional alternatives "+ifTrue.prettyPrint()+" and "+
            ifNot.prettyPrint()+"-> Assuming "+unitType.prettyPrint();
        expr.setType(Either.value(unitType));
        Log.warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }

      //both are numeric primitives (and not equal) ergo one is real and one is integer -> real
      if(isNumericPrimitive(ifTrue)&&isNumericPrimitive(ifNot)){
        expr.setType(Either.value(getRealType()));
        return;
      }

      //if we get here it is an error
      final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
          "Mismatched conditional alternatives "+ifTrue.prettyPrint()+" and "+
          ifNot.prettyPrint()+".";
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg,expr.get_SourcePositionStart());
      return;
    }
  }
}
