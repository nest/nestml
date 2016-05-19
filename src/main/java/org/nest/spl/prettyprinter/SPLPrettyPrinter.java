/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.prettyprinter;

import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import de.se_rwth.commons.Names;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.spl._ast.*;
import org.nest.spl._visitor.SPLVisitor;
import org.nest.utils.ASTNodes;
import org.nest.utils.PrettyPrinterBase;

import java.util.List;

import static de.se_rwth.commons.Names.getQualifiedName;

/**
 * Produces the concrete textual representation from the AST.
 *
 * @author plotnikov
 */
public class SPLPrettyPrinter extends PrettyPrinterBase implements SPLVisitor {

  private final ExpressionsPrettyPrinter expressionsPrettyPrinter;


  protected SPLPrettyPrinter(final ExpressionsPrettyPrinter expressionsPrettyPrinter) {
    this.expressionsPrettyPrinter = expressionsPrettyPrinter;
  }

  public void print(final ASTSPLNode node) {
    node.accept(this);
  }

  /**
   * Grammar
   * SPLFile = ModuleDefinitionStatement Block;
   */
  @Override
  public void visit(final ASTSPLFile astFile) {
    // at the moment do nothing
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
   *   IF_Stmt = IF_Clause
   *             ELIF_Clause*
   *             (ELSE_Clause)?
   *             BLOCK_CLOSE;
   */
  @Override
  public void endVisit(final ASTIF_Stmt node) {
    println(BLOCK_CLOSE);
  }

  /**
   * Grammar:
   *   IF_Clause = "if" Expr BLOCK_OPEN Block;
   */
  @Override
  public void visit(final ASTIF_Clause astIfClause) {
    print("if" + " ");
    final String conditionExpression = expressionsPrettyPrinter.print(astIfClause.getExpr());
    println(conditionExpression + BLOCK_OPEN);
    indent();
  }

  @Override
  public void endVisit(final ASTIF_Clause astIfClause) {
    unindent();
  }

  /**
   * ELIF_Clause = "elif" Expr BLOCK_OPEN Block;
   */
  @Override
   public void visit(final ASTELIF_Clause astElifNode) {
    print("elif" + " ");
    final String conditionExpression = expressionsPrettyPrinter.print(astElifNode.getExpr());
    println(conditionExpression + BLOCK_OPEN);
    indent();
  }

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
    println("else:");
    indent();
  }

  @Override
  public void endVisit(final ASTELSE_Clause astElseClause) {
    unindent();
  }

  /**
   * Small_Stmt = Assignment
   * | FunctionCall
   * | Declaration
   * | ReturnStmt;
   */
  @Override
  public void visit(final ASTSmall_Stmt astSmallStmt ) {
    if (astSmallStmt.getAssignment().isPresent()) {
      printAssignment(astSmallStmt.getAssignment().get());
    } else if (astSmallStmt.getFunctionCall().isPresent()) {
      printFunctionCall(astSmallStmt.getFunctionCall().get());
    }  else if (astSmallStmt.getDeclaration().isPresent()) {
      printDeclaration(astSmallStmt.getDeclaration().get());
    }  else if (astSmallStmt.getReturnStmt().isPresent()) {
      printReturnStatement(astSmallStmt.getReturnStmt().get());
    }

  }


  /**
   * Small_Stmt = Assignment
   * | FunctionCall
   * | Declaration
   * | ReturnStmt;
   */
  @Override
  public void endVisit(final ASTSmall_Stmt astSmallStmt ) {
    println();
  }

  /**
   * Grammar:
   * Assignment = variableName:QualifiedName "=" Expr;
   */
  public void printAssignment(final ASTAssignment astAssignment) {
    final String lhsVariableName = astAssignment.getLhsVarialbe();
    final String rhsOfAssignment = expressionsPrettyPrinter.print(astAssignment.getExpr());
    if (astAssignment.isAssignment()) {
      println(lhsVariableName + " = " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundSum()) {
      println(lhsVariableName + " += " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundMinus()) {
      println(lhsVariableName + " -= " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundProduct()) {
      println(lhsVariableName + " *= " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundQuotient()) {
      println(lhsVariableName + " /= " + rhsOfAssignment);
    }


  }

  /**
   * Grammar:
   * FunctionCall = QualifiedName "(" ArgList ")";
   * ArgList = (args:Expr ("," args:Expr)*)?;
   */
  public void printFunctionCall(final ASTFunctionCall astFunctionCall) {
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
    println();
  }

  /**
   * ReturnStmt = "return" Expr?;
   */
  public void printReturnStatement(final ASTReturnStmt astReturnStmt) {

    if (astReturnStmt.getExpr().isPresent()) {
      final String returnExpressionAsString = expressionsPrettyPrinter.print(astReturnStmt.getExpr().get());
      println("return " + returnExpressionAsString);
    }
    else {
      println("return");
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
    print(ASTNodes.computeTypeName(astDeclaration.getDatatype()));
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
      print(createPrettyPrinterForTypes().prettyprint(astForStmt.getStep().get()));
    }
    println(BLOCK_OPEN);
    indent();
  }

  @Override
  public void endVisit(final ASTFOR_Stmt node) {
    unindent();
    println(BLOCK_CLOSE);
  }

  /**
   * Grammar:
   * WHILE_Stmt = "while" Expr BLOCK_OPEN Block BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTWHILE_Stmt astWhileStmt) {
    print("while ");
    print(expressionsPrettyPrinter.print(astWhileStmt.getExpr()));
    println(BLOCK_OPEN);
    indent();
  }

  @Override
  public void endVisit(final ASTWHILE_Stmt node) {
    unindent();
    println(BLOCK_CLOSE);
  }

  private TypesPrettyPrinterConcreteVisitor createPrettyPrinterForTypes() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }

}
