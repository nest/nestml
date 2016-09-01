package org.nest.commons._ast;

import de.monticore.literals.literals._ast.ASTBooleanLiteral;
import de.monticore.literals.literals._ast.ASTStringLiteral;
import org.nest.commons._visitor.ExpressionTypeVisitor;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import java.util.Optional;

/**
 * @author ptraeder
 */
public class ASTExpr extends ASTExprTOP {

  private Optional<Either<TypeSymbol,String>> type = Optional.empty();

  private void doComputeType() {
//    checkArgument(getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");

    if(!type.isPresent()){
      //no type set yet. Run Visitor.
      ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
      accept(expressionTypeVisitor);
    }

    //Just to be sure. Should never happen
    if(!type.isPresent()){
      final String errorMsg = "This operation for expressions is not supported yet.";
      type= Optional.of(Either.error(errorMsg));
    }

    //Handle unitless expressions by returning real type instead
    if(type.get().isValue()){
      TypeSymbol typeSymbol = type.get().getValue();
      if(typeSymbol.getType() == TypeSymbol.Type.UNIT){
        UnitRepresentation unit = new UnitRepresentation(typeSymbol.getName());
        if(unit.isZero()){
         type =Optional.of(Either.value(PredefinedTypes.getRealType()));
        }
      }
    }
  }
  public Optional<Either<TypeSymbol,String>> computeType(){
    if(!type.isPresent()) {
      doComputeType();
    }
    return type;
  }


  public Optional<Either<TypeSymbol,String>> getType(){
    return type;
  }
  public void setType(Either<TypeSymbol,String> type) {
    this.type = Optional.of(type);
  }


  public ASTExpr(){}

  public ASTExpr(ASTExpr base,
  ASTExpr exponent,
  ASTExpr term,
  ASTExpr expr,
  ASTExpr left,
  ASTExpr right,
  ASTExpr condition,
  ASTExpr ifTure,
  ASTExpr ifNot,
  ASTFunctionCall functionCall,
  ASTBooleanLiteral booleanLiteral,
  ASTNESTMLNumericLiteral nESTMLNumericLiteral,
  ASTStringLiteral stringLiteral,
  ASTVariable variable,
  boolean inf,
  boolean logicalOr,
  boolean logicalAnd,
  boolean logicalNot,
  boolean gt,
  boolean ge,
  boolean ne2,
  boolean ne,
  boolean eq,
  boolean le,
  boolean lt,
  boolean bitOr,
  boolean bitXor,
  boolean bitAnd,
  boolean shiftRight,
  boolean shiftLeft,
  boolean minusOp,
  boolean plusOp,
  boolean moduloOp,
  boolean divOp,
  boolean timesOp,
  boolean unaryTilde,
  boolean unaryMinus,
  boolean unaryPlus,
  boolean pow,
  boolean leftParentheses,
  boolean rightParentheses)  {

    super(base,exponent,term,expr,left,right,condition,ifTure,ifNot,functionCall,booleanLiteral,nESTMLNumericLiteral,stringLiteral,
        variable,inf,logicalOr,logicalAnd,logicalNot,gt,ge,ne2,ne,eq,le,lt,bitOr,bitXor,bitAnd,shiftRight,shiftLeft,minusOp,
        plusOp,moduloOp,divOp,timesOp,unaryTilde,unaryMinus,unaryPlus,pow,leftParentheses,rightParentheses);
  }


}
