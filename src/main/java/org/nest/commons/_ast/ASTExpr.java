package org.nest.commons._ast;

import java.util.Optional;

import de.monticore.literals.literals._ast.ASTBooleanLiteral;
import de.monticore.literals.literals._ast.ASTStringLiteral;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * @author ptraeder
 */
public class ASTExpr extends ASTExprTOP {

  private Optional<Either<TypeSymbol,String>> type = Optional.empty();

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
