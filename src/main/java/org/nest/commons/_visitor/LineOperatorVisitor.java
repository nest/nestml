package org.nest.commons._visitor;

import com.google.common.base.Joiner;
import de.monticore.literals.literals._ast.ASTFloatLiteral;
import de.monticore.literals.literals._ast.ASTNumericLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTNESTMLNumericLiteral;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static java.lang.Math.pow;
import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class LineOperatorVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_LINE_OPERATOR_VISITOR";

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
          if(isUnit(rhsType)){
            UnitRepresentation rhsRep = UnitRepresentation.getBuilder().serialization(rhsType.getName()).build();
            if(rhsRep.isIgnoreMagnitude()){
              expr.setType(Either.value(rhsType));
            }else{
              expr.setType(Either.value(lhsType));
            }
          }else{
            expr.setType(Either.value(lhsType)); //no units involved, any is valid
          }
          return;
      }
      //both numeric primitive, not matching -> 1 real one integer -> real
      if (isNumericPrimitive(lhsType)&&isNumericPrimitive(rhsType)) {
        expr.setType(Either.value(getRealType()));
        return;
      }
      //Both are units, not matching -> see if matching base
      if(isUnit(lhsType)&&isUnit(rhsType)){
        //Base not matching -> error
        UnitRepresentation rhsRep = UnitRepresentation.getBuilder().serialization(rhsType.getName()).build();
        UnitRepresentation lhsRep = UnitRepresentation.getBuilder().serialization(lhsType.getName()).build();
        if(!lhsRep.equalBase(rhsRep)) {
          final String errorMsg = ERROR_CODE + " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
              "Addition/substraction of " + lhsType.prettyPrint() + " and " + rhsType.prettyPrint() +
              ". Assuming real.";
          expr.setType(Either.value(getRealType()));
          warn(errorMsg, expr.get_SourcePositionStart());
          return;
        }else{//Base matching, install conversion
          //Determine the "greater" unit of the two and the difference in magnitude
          ASTExpr bigger;
          int magDiff;
          boolean leftIsBigger;
          if(lhsRep.hasBiggerMagnitudeThan(rhsRep)){
            bigger = expr.getLeft().get();
            magDiff = lhsRep.getMagnitude() - rhsRep.getMagnitude();
            leftIsBigger = true;
          }
          else{
            bigger = expr.getRight().get();
            magDiff = rhsRep.getMagnitude() - lhsRep.getMagnitude();
            leftIsBigger = false;
          }
          double literalSource = pow(10.0,magDiff);

          checkState(magDiff%3 == 0,"Difference between magnitudes not a multiple of 3"); // should never be a problem

          //create expression holding literal node to switch value and magnitude
          ASTFloatLiteral conversionFloatLiteral = ASTFloatLiteral.getBuilder().
              source(String.valueOf(literalSource)).build();
          ASTNESTMLNumericLiteral conversionFinishedLiteral = ASTNESTMLNumericLiteral.getBuilder().
              numericLiteral(conversionFloatLiteral).build();
          ASTExpr conversionLiteralExpr = ASTExpr.getBuilder().nESTMLNumericLiteral(conversionFinishedLiteral).build();
          TypeSymbol magType = new TypeSymbol("[0,0,0,0,0,0,0,"+(-magDiff)+"]i", TypeSymbol.Type.UNIT);
          conversionLiteralExpr.setType(Either.value(magType));

          //create multiplication node
          ASTExpr substitute = ASTExpr.getBuilder().left(bigger).right(conversionLiteralExpr).timesOp(true).build();

          //replace "bigger" expression with multiplication
          if(leftIsBigger){
            expr.setLeft(substitute);
          }else{
            expr.setRight(substitute);
          }

          //Visit newly created sub-tree
          ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
          expr.accept(expressionTypeVisitor);
          return;

        }
      }
      //one is unit and one numeric primitive and vice versa -> assume unit, warn
      if((isUnit(lhsType)&&isNumericPrimitive(rhsType))||
      (isUnit(rhsType)&&isNumericPrimitive(lhsType))){
        TypeSymbol unitType;
        if(isUnit(lhsType)){
          unitType = lhsType;
        }else{
          unitType = rhsType;
        }
        final String errorMsg =ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
            "Addition/substraction of "+lhsType.prettyPrint()+" and "+rhsType.prettyPrint()+
            ". Assuming "+unitType.prettyPrint();
        expr.setType(Either.value(unitType));
        warn(errorMsg,expr.get_SourcePositionStart());
        return;
      }
    }

    //If a buffer is involved, the other unit takes precedent TODO: is this the intended semantic?
    if(lhsType == getBufferType()){
      expr.setType(Either.value(rhsType));
      return;
    }
    if(rhsType == getBufferType()){
      expr.setType(Either.value(lhsType));
      return;
    }

    //if we get here, we are in a general error state
    final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
        "Cannot determine the type of "+ (expr.isPlusOp()?"addition":"substraction")+" with types: " +
        lhsType.prettyPrint()+ " and " + rhsType.prettyPrint();
    expr.setType(Either.error(errorMsg));
    error(errorMsg,expr.get_SourcePositionStart());
    return;
  }
}
