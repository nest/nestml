/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.prettyprinter;

import de.monticore.ast.ASTNode;
import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import org.nest.commons._ast.ASTBLOCK_CLOSE;
import org.nest.commons._ast.ASTBLOCK_OPEN;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLVisitor;
import org.nest.utils.ASTUtils;
import org.nest.utils.PrettyPrinterBase;

import java.util.List;
import java.util.Optional;

import static de.se_rwth.commons.Names.getQualifiedName;

/**
 * Produces the concrete textual representation from the AST.
 *
 * @author plotnikov
 */
public class SPLPrettyPrinter extends PrettyPrinterBase implements SPLVisitor {
  private final ExpressionsPrettyPrinter expressionsPrettyPrinter;
  private ASTSPLNode root;

  protected SPLPrettyPrinter(final ExpressionsPrettyPrinter expressionsPrettyPrinter) {
    this.expressionsPrettyPrinter = expressionsPrettyPrinter;
  }

  public void print(final ASTSPLNode node) {
    root = node;
    node.accept(this);

  }

  /**
   * ModuleDefinitionStatement = "module" moduleName:QualifiedName;
   */
  @Override
  public void visit(final ASTModuleDefinitionStatement node) {
    final String moduleName = getQualifiedName(node.getModuleName().getParts());
    println("module " + moduleName);
  }

  /**
   * Grammar:
   *   IF_Clause = "if" Expr BLOCK_OPEN Block;
   */
  @Override
  public void visit(final ASTIF_Clause astIfClause) {
    print("if" + " ");
    final String conditionExpression = expressionsPrettyPrinter.print(astIfClause.getExpr());
    print(conditionExpression);
  }

  /**
   * This method unidents the output.
   */
  @Override
  public void endVisit(final ASTIF_Clause astIfClause) {
    Optional<ASTNode> parent = ASTUtils.getParent(astIfClause, root);
    if (parent.isPresent() && parent.get() instanceof ASTIF_Stmt) {
      final ASTIF_Stmt astIfStmt = (ASTIF_Stmt) parent.get();
      final boolean isSingleIfClause = !astIfStmt.getELSE_Clause().isPresent() && astIfStmt.getELIF_Clauses().isEmpty();
      // any other form of if clause ends with an 'end' keyword and is handled in the corresponding visit method.
      if (!isSingleIfClause) {
        unindent();
      }

    }

  }

  /**
   * ELIF_Clause = "elif" Expr BLOCK_OPEN Block;
   */
  @Override
   public void visit(final ASTELIF_Clause astElifNode) {
    print("elif" + " ");
    final String conditionExpression = expressionsPrettyPrinter.print(astElifNode.getExpr());
    print(conditionExpression);
  }

  /**
   * Doesn't terminate with 'end' and must be unindented manually
   */
  @Override
  public void endVisit(final ASTELIF_Clause astElifNode) {
    unindent();
  }

  /**
   * Grammar:
   * ELSE_Clause = "else" BLOCK_OPEN Block;
   */
  @Override
  public void visit(final ASTELSE_Clause astElseClause) {
    print("else");
  }

  @Override
  public void visit(final ASTSimple_Stmt astSimpleStmt ) {
    final String comment = ASTUtils.printComments(astSimpleStmt);
    if (!comment.isEmpty()) {
      println(comment);
    }

  }

  @Override
  public void visit(final ASTStmt astStmt) {
    final String comment = ASTUtils.printComments(astStmt);
    if (!comment.isEmpty()) {
      println(comment);
    }

  }

  /**
   * Small_Stmt = Assignment| FunctionCall | Declaration | ReturnStmt;
   */
  @Override
  public void visit(final ASTSmall_Stmt astSmallStmt ) {
    print(ASTUtils.printComments(astSmallStmt));

    if (astSmallStmt.getAssignment().isPresent()) {
      printAssignment(astSmallStmt.getAssignment().get());
    } else if (astSmallStmt.getFunctionCall().isPresent()) {
      printFunctionCall(astSmallStmt.getFunctionCall().get());
    }  else if (astSmallStmt.getDeclaration().isPresent()) {
      printDeclaration(astSmallStmt.getDeclaration().get());
    }  else if (astSmallStmt.getReturnStmt().isPresent()) {
      printReturnStatement(astSmallStmt.getReturnStmt().get());
    }
    println();
  }

  /**
   * Grammar:
   * Assignment = variableName:QualifiedName "=" Expr;
   */
  private void printAssignment(final ASTAssignment astAssignment) {
    final String lhsVariableName = astAssignment.getLhsVarialbe().toString();
    final String rhsOfAssignment = expressionsPrettyPrinter.print(astAssignment.getExpr());
    if (astAssignment.isAssignment()) {
      print(lhsVariableName + " = " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundSum()) {
      print(lhsVariableName + " += " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundMinus()) {
      print(lhsVariableName + " -= " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundProduct()) {
      print(lhsVariableName + " *= " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundQuotient()) {
      print(lhsVariableName + " /= " + rhsOfAssignment);
    }

  }

  /**
   * Grammar:
   * FunctionCall = QualifiedName "(" ArgList ")";
   * ArgList = (args:Expr ("," args:Expr)*)?;
   */
  private void printFunctionCall(final ASTFunctionCall astFunctionCall) {
    final String functionName = astFunctionCall.getCalleeName();
    print(functionName + "(");
    final List<ASTExpr> functionArguments = astFunctionCall.getArgs();
    for (int argumentIndex = 0; argumentIndex < functionArguments.size(); ++argumentIndex) {
      boolean isLastFunctionArgument = (argumentIndex + 1) == functionArguments.size();
      final ASTExpr currentArgument = functionArguments.get(argumentIndex);
      print(expressionsPrettyPrinter.print(currentArgument));
      if (!isLastFunctionArgument) {
        print(", ");
      }

    }
    print(")");
  }

  /**
   * ReturnStmt = "return" Expr?;
   */
  private void printReturnStatement(final ASTReturnStmt astReturnStmt) {

    if (astReturnStmt.getExpr().isPresent()) {
      final String returnExpressionAsString = expressionsPrettyPrinter.print(astReturnStmt.getExpr().get());
      print("return " + returnExpressionAsString);
    }
    else {
      print("return");
    }

  }

  /**
   * Grammar
   * Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
   */
  public void printDeclaration(final ASTDeclaration astDeclaration) {
    printDeclarationVariables(astDeclaration);
    printDeclarationType(astDeclaration);
    printOptionalInitializationExpression(astDeclaration);

  }

  private void printDeclarationVariables(final ASTDeclaration astDeclaration) {
    final List<String> variableNames = astDeclaration.getVars();
    for (int variableIndex = 0; variableIndex < variableNames.size(); ++ variableIndex) {
      boolean isLastVariableInDeclaration = (variableIndex + 1) == variableNames.size();

      print(variableNames.get(variableIndex));
      if (!isLastVariableInDeclaration) {
        print(", ");
      }

    }

    print(" ");
  }

  private void printDeclarationType(final ASTDeclaration astDeclaration) {
    print(ASTUtils.computeTypeName(astDeclaration.getDatatype(),true));
    if (astDeclaration.getSizeParameter().isPresent()) {
      print(" [" + astDeclaration.getSizeParameter().get() + "]");
    }

  }

  private void printOptionalInitializationExpression(final ASTDeclaration astDeclaration) {
    if (astDeclaration.getExpr().isPresent()) {
      print(" = " + expressionsPrettyPrinter.print(astDeclaration.getExpr().get()));
    }

  }

  /**
   * Grammar:
   * FOR_Stmt = "for" var:Name "in" from:Expr "..." to:Expr ("step" step:SignedNumericLiteral)?
   *            BLOCK_OPEN Block BLOCK_CLOSE;
   */
  @Override public void visit(final ASTFOR_Stmt astForStmt) {
    print("for ");
    print(astForStmt.getVar());
    print(" in ");
    print(expressionsPrettyPrinter.print(astForStmt.getFrom()));
    print(" ... ");
    print(expressionsPrettyPrinter.print(astForStmt.getTo()));
    if (astForStmt.getStep().isPresent()) {
      print(" step ");
      print(typesPrinter().prettyprint(astForStmt.getStep().get()));
    }
  }

  /**
   * Grammar:
   * WHILE_Stmt = "while" Expr BLOCK_OPEN Block BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTWHILE_Stmt astWhileStmt) {
    print("while ");
    print(expressionsPrettyPrinter.print(astWhileStmt.getExpr()));
  }

  @Override
  public void visit(final ASTBlock astBlock ) {
    final String comment = ASTUtils.printComments(astBlock);
    if (!comment.isEmpty()) {
      println(comment);
    }
  }

  @Override
  public void visit(final ASTBLOCK_OPEN astBlockOpen) {
    final String comment = ASTUtils.printComments(astBlockOpen);
    if (comment.isEmpty()) {
      println(BLOCK_OPEN);
    }
    else {
      println(BLOCK_OPEN + " " + comment);
    }
    indent();

  }

  @Override
  public void endVisit(final ASTBLOCK_CLOSE astBlockClose) {
    unindent();
    final String comment = ASTUtils.printComments(astBlockClose);
    if (comment.isEmpty()) {
      println(BLOCK_CLOSE);
    }
    else {
      println(BLOCK_CLOSE + " " +  comment);
    }

  }

  private TypesPrettyPrinterConcreteVisitor typesPrinter() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }

}
