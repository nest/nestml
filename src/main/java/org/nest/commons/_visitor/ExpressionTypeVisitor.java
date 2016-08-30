package org.nest.commons._visitor;

import static org.nest.symboltable.predefined.PredefinedTypes.*;

import java.util.Optional;
import java.util.Stack;

import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * @author ptraeder, plotnikov
 */
public class ExpressionTypeVisitor implements CommonsVisitor {

 /* static final Stack<CommonsVisitor> callStack = new Stack<>();

  public Optional<CommonsVisitor> getCaller() {
    if (!callStack.isEmpty()) {
      CommonsVisitor topElement = (CommonsVisitor) callStack.peek();
      return Optional.of(topElement);
    }
    // no parent, return an absent value
    return Optional.empty();
  }

  public void endVisit(ASTExpr node){
    //restore previous realthis pointer
    if(!callStack.isEmpty())
      setRealThis(callStack.pop());
  }*/

  private CommonsVisitor realThis=this;

  private static UnaryVisitor unaryVisitor = new UnaryVisitor();
  private static PowVisitor powVisitor = new PowVisitor();
  private static ParenthesesVisitor parenthesesVisitor = new ParenthesesVisitor();
  private static LogicalNotVisitor logicalNotVisitor = new LogicalNotVisitor();
  private static DotOperatorVisitor dotOperatorVisitor = new DotOperatorVisitor();
  private static LineOperatorVisitor lineOperatorVisitor = new LineOperatorVisitor();
  private static NoSemantics noSemantics = new NoSemantics();
  private static ComparisonOperatorVisitor comparisonOperatorVisitor = new ComparisonOperatorVisitor();
  private static BinaryLogicVisitor binaryLogicVisitor = new BinaryLogicVisitor();
  private static ConditionVisitor conditionVisitor = new ConditionVisitor();
  private static FunctionCallVisitor functionCallVisitor = new FunctionCallVisitor();
  private static BooleanLiteralVisitor booleanLiteralVisitor = new BooleanLiteralVisitor();
  private static NESTMLNumericLiteralVisitor nESTMLNumericLiteralVisitor = new NESTMLNumericLiteralVisitor();
  private static StringLiteralVisitor stringLiteralVisitor = new StringLiteralVisitor();
  private static VariableVisitor variableVisitor = new VariableVisitor();
  private static InfVisitor infVisitor = new InfVisitor();


  public void handle(org.nest.commons._ast.ASTExpr node) {
    traverse(node);
    getRealThis().visit(node);
    endVisit(node);
  }

  @Override
  public CommonsVisitor getRealThis() {
    return realThis;
  }

  @Override
  public void setRealThis(CommonsVisitor realThis) {
      this.realThis = realThis;
  }


  public void traverse(org.nest.commons._ast.ASTExpr node) {
   // callStack.push(getRealThis());

    //Expr = <rightassoc> base:Expr pow:["**"] exponent:Expr
    if (node.getBase().isPresent() && node.getExponent().isPresent()) {
      node.getBase().get().accept(this);
      node.getExponent().get().accept(this);
      setRealThis(powVisitor);
      return;
    }

    //Expr = (unaryPlus:["+"] | unaryMinus:["-"] | unaryTilde:["~"]) term:Expr
    if (node.getTerm().isPresent()) {
      node.getTerm().get().accept(this);
      setRealThis(unaryVisitor);
      return;
    }

    //Parentheses and logicalNot
    if (node.getExpr().isPresent()) {
      node.getExpr().get().accept(this);

      //Expr = leftParentheses:["("] Expr rightParentheses:[")"]
      if(node.isLeftParentheses() && node.isRightParentheses()){
        setRealThis(parenthesesVisitor);
        return;
      }
      //Expr = logicalNot:["not"] Expr
      if(node.isLogicalNot()){
        setRealThis(logicalNotVisitor);
        return;
      }
    }

    //Rules with Left/Right expressions
    if (node.getLeft().isPresent() && node.getRight().isPresent()) {
      node.getLeft().get().accept(this);
      node.getRight().get().accept(this);

      //Expr = left:Expr (timesOp:["*"] | divOp:["/"] | moduloOp:["%"]) right:Expr
      if(node.isTimesOp() || node.isDivOp() || node.isModuloOp()){
        setRealThis(dotOperatorVisitor);
        return;
      }
      //Expr = left:Expr (plusOp:["+"] | minusOp:["-"]) right:Expr
      if(node.isPlusOp() || node.isMinusOp()){
        setRealThis(lineOperatorVisitor);
        return;
      }
      //Expr = left:Expr (shiftLeft:["<<"] | shiftRight:[">>"]) right:Expr
      if(node.isShiftLeft() || node.isShiftRight()){
        setRealThis(noSemantics); //TODO: implement something
        return;
      }
      //Expr = left:Expr (bitAnd:["&"] | bitXor:["^"] | bitOr:["|"]) right:Expr
      if(node.isBitAnd() || node.isBitOr() || node.isBitXor()){
        setRealThis(noSemantics); //TODO: implement something
        return;
      }
      //Expr = left:Expr (lt:["<"] | le:["<="] | eq:["=="]
      // | ne:["!="] | ne2:["<>"] | ge:[">="] | gt:[">"]) right:Expr
      if(node.isLt() || node.isLe() || node.isEq() || node.isNe() ||
          node.isNe2() || node.isGe() || node.isGt()){
        setRealThis(comparisonOperatorVisitor);
        return;
      }
      //Expr = left:Expr (logicalAnd:["and"] | logicalOr:["or"]) right:Expr
      if(node.isLogicalAnd() || node.isLogicalOr()){
        setRealThis(binaryLogicVisitor);
        return;
      }
    }

    //Expr = condition:Expr "?" ifTrue:Expr ":" ifNot:Expr
    if (node.getCondition().isPresent() && node.getIfTrue().isPresent() && node.getIfNot().isPresent()){
      node.getCondition().get().accept(this);
      node.getIfTrue().get().accept(this);
      node.getIfNot().get().accept(this);
      setRealThis(conditionVisitor);
      return;
    }

    //Expr = FunctionCall
    if (node.getFunctionCall().isPresent()) {
      //node.getFunctionCall().get().accept(this);
      setRealThis(functionCallVisitor);
      return;
    }

    //Expr = BooleanLiteral
    if (node.getBooleanLiteral().isPresent()) {
      //node.getBooleanLiteral().get().accept(this);
      setRealThis(booleanLiteralVisitor);
      return;
    }

    //Expr = NESTMLNumericLiteral
    if (node.getNESTMLNumericLiteral().isPresent()) {
     // node.getNESTMLNumericLiteral().get().accept(this);
      setRealThis(nESTMLNumericLiteralVisitor);
      return;
    }

    //Expr = StringLiteral
    if (node.getStringLiteral().isPresent()) {
     // node.getStringLiteral().get().accept(this);
      setRealThis(stringLiteralVisitor);
      return;
    }

    //Expr = Variable
    if (node.getVariable().isPresent()) {
     // node.getVariable().get().accept(this);
      setRealThis(variableVisitor);
      return;
    }

    //Expr = ["inf"]
    if (node.isInf()){
      setRealThis(infVisitor);
      return;
    }



  }

  //Helper functions:


  public static Either<Integer, String> calculateNumericValue(ASTExpr expr) {
    if (expr.isLeftParentheses()) {
      return calculateNumericValue(expr.getExpr().get());
    }
    else if (expr.getNESTMLNumericLiteral().isPresent()) {
      if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
        ASTIntLiteral literal = (ASTIntLiteral) expr.getNESTMLNumericLiteral().get().getNumericLiteral();
        return Either.value(literal.getValue());
      }
      else {
        return Either.error("No floating point values allowed in the exponent to a UNIT base");
      }
    }
    else if (expr.isUnaryMinus()) {
      Either<Integer, String> term = calculateNumericValue(expr.getTerm().get());
      if (term.isError()) {
        return term;
      }
      return Either.value(-term.getValue());
    }

    return Either.error("Cannot calculate value of exponent. Must be a static value!");
  }

  public static void handleDefaultError(ASTExpr expr){
    if(!expr.getType().isPresent()){
      String msg = "Cannot determine the type of the Expression-Node @<"
          + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();
      expr.setType(Either.error(msg));
    }
  }
  /**
   * Checks if the type is a numeric type, e.g. Integer or Real.
   */
  public static boolean isNumeric(final TypeSymbol type) {
    return type.equals(getIntegerType()) ||
        type.equals(getRealType()) ||
        type.getType().equals(TypeSymbol.Type.UNIT);

  }


}

