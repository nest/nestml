package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

import static org.nest.symboltable.typechecking.TypeChecker.isNumericPrimitive;
import static org.nest.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * @author ptraeder
 */
public class ConditionVisitor implements CommonsVisitor {

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
        final String errorMsg = CommonsErrorStrings.messageTernary(this, expr.get_SourcePositionStart());
        expr.setType(Either.error(errorMsg));
        Log.error(errorMsg, expr.get_SourcePositionStart());
        return;
      }
      //Alternatives match exactly -> any is valid
      if (ifTrue.prettyPrint().equals(ifNot.prettyPrint())) {
        expr.setType(Either.value(ifTrue));
        return;
      }

      //Both are units -> real
      if (isUnit(ifTrue) && isUnit(ifNot)) {
        final String errorMsg = CommonsErrorStrings.messageTrueNot(
            this,
            ifTrue.prettyPrint(),
            ifNot.prettyPrint(),
            expr.get_SourcePositionStart());
        expr.setType(Either.value(getRealType()));
        Log.warn(errorMsg, expr.get_SourcePositionStart());
        return;
      }
      //one Unit and one numeric primitive and vice versa -> assume unit,warn
      if ((isUnit(ifTrue) && isNumericPrimitive(ifNot)) ||
          isUnit(ifNot) && isNumericPrimitive(ifTrue)) {
        TypeSymbol unitType;
        if (isUnit(ifTrue)) {
          unitType = ifTrue;
        }
        else {
          unitType = ifNot;
        }
        final String errorMsg = CommonsErrorStrings.messageTrueNot(
            this,
            ifTrue.prettyPrint(),
            ifNot.prettyPrint(),
            expr.get_SourcePositionStart());
        expr.setType(Either.value(unitType));
        Log.warn(errorMsg, expr.get_SourcePositionStart());
        return;
      }

      //both are numeric primitives (and not equal) ergo one is real and one is integer -> real
      if (isNumericPrimitive(ifTrue) && isNumericPrimitive(ifNot)) {
        expr.setType(Either.value(getRealType()));
        return;
      }

      //if we get here it is an error
      final String errorMsg = CommonsErrorStrings.messageTrueNot(
          this,
          ifTrue.prettyPrint(),
          ifNot.prettyPrint(),
          expr.get_SourcePositionStart());
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg, expr.get_SourcePositionStart());
    }

  }

}
