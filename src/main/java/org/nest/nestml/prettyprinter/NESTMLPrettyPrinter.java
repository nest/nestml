/*
* Copyright (c) 2015 RWTH Aachen. All rights reserved.
*
* http://www.se-rwth.de/
*/
package org.nest.nestml.prettyprinter;

import de.monticore.ast.ASTNode;
import de.monticore.ast.Comment;
import de.monticore.prettyprint.CommentPrettyPrinter;
import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.utils.AstUtils;
import org.nest.utils.PrettyPrinterBase;

import java.util.List;
import java.util.Optional;

import static org.nest.nestml._symboltable.typechecking.TypeChecker.deserializeUnitIfNotPrimitive;
import static org.nest.utils.AstUtils.printComments;

/**
 * Provides convenient  functions to statically type interfaces ast-nodes resulting from the Body-grammar
 * production.
 *
 * @author plotnikov
 */
public class NESTMLPrettyPrinter implements NESTMLInheritanceVisitor {
  private static final String BLOCK_CLOSE = "end";
  private static final String BLOCK_OPEN = ":";
  private final ExpressionsPrettyPrinter expressionsPrinter;
  private final ASTNESTMLNode root;
  private final IndentPrinter printer = new IndentPrinter();

  private NESTMLPrettyPrinter(final ASTNESTMLNode root) {
    this.expressionsPrinter = new ExpressionsPrettyPrinter();
    this.root = root;
  }

  public static String print(final ASTNESTMLNode astNestmlNode) {
    final NESTMLPrettyPrinter prettyPrinter = new NESTMLPrettyPrinter(astNestmlNode);
    astNestmlNode.accept(prettyPrinter);
    return prettyPrinter.printer.getContent();
  }

  ////////////////////////////////////////////////////////////////////////////
  // NESTML PART
  ////////////////////////////////////////////////////////////////////////////

  /**
   * Neuron = "neuron" Name
     BLOCK_OPEN
       (NEWLINE |
        BlockWithVariables |
        UpdateBlock |
        Equations |
        Input |
        Output |
        Function)*
     BLOCK_CLOSE;
   * @param astNeuron
   */
  @Override
  public void handle(final ASTNeuron astNeuron) {
    CommentPrettyPrinter.printPreComments(astNeuron, printer);

    printer.println("neuron " + astNeuron.getName() + BLOCK_OPEN);
    printer.indent();

    printNodes(astNeuron.getBlockWithVariabless());
    printNodes(astNeuron.getUpdateBlocks());
    printNodes(astNeuron.getEquationss());
    printNodes(astNeuron.getInputs());
    printNodes(astNeuron.getOutputs());
    printNodes(astNeuron.getFunctions());

    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPostComments(astNeuron, printer);
  }

  @Override
  public void handle(final ASTBlockWithVariables astBlockWithVariables) {
    CommentPrettyPrinter.printPreComments(astBlockWithVariables, printer);

    printBlockKeyword(astBlockWithVariables);
    printer.indent();

    astBlockWithVariables.getDeclarations().forEach(node -> node.accept(this));

    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPostComments(astBlockWithVariables, printer);
  }

  private void printBlockKeyword(final ASTBlockWithVariables astVarBlock) {
    if (astVarBlock.isState()) {
      printer.println("state" + BLOCK_OPEN);
    }
    else if (astVarBlock.isInternals()) {
      printer.println("internals" + BLOCK_OPEN);
    }
    else if (astVarBlock.isParameters ()) {
      printer.println("parameters" + BLOCK_OPEN);
    }

  }

  public void handle(final ASTUpdateBlock astUpdateBlock) {
    printer.println("update" + BLOCK_OPEN);
    printer.indent();
    printNode(astUpdateBlock.getBlock());
    printer.unindent();
    printer.println(BLOCK_CLOSE);
  }

  private void printNodes(final List<? extends ASTNESTMLNode> nodes) {
    for (ASTNESTMLNode node:nodes) {
      printNode(node);
    }
  }

  private void printNode(ASTNESTMLNode node) {
      node.accept(this);
  }

  ////////////////////////////////////////////////////////////////////////////
  // SPL PART
  ////////////////////////////////////////////////////////////////////////////
  public void handle(final ASTDeclaration astDeclaration) {
    astDeclaration.getDocStrings().forEach(printer::println);

    printAliasPrefix(astDeclaration);
    printDeclarationVariables(astDeclaration);
    printDeclarationType(astDeclaration);
    printOptionalInitializationExpression(astDeclaration);
    printInvariants(astDeclaration);
    CommentPrettyPrinter.printPostComments(astDeclaration, printer);
    printer.println();
  }

  private void printAliasPrefix(final ASTDeclaration astAliasDecl) {
    if (astAliasDecl.isRecordable()) {
      printer.print("recordable ");
    }

    if (astAliasDecl.isFunction()) {
      printer.print("function ");
    }
  }

  private void printInvariants(final ASTDeclaration astAliasDecl) {
    if (astAliasDecl.getInvariant().isPresent()) {
      printer.print("[[");
      final ASTExpr astInvariant = astAliasDecl.getInvariant().get();
      printer.print(expressionsPrinter.print(astInvariant));
      printer.print("]]");

    }
  }


  private void printDeclarationVariables(final ASTDeclaration astDeclaration) {
    final List<ASTVariable> variableNames = astDeclaration.getVars();
    for (int variableIndex = 0; variableIndex < variableNames.size(); ++ variableIndex) {
      boolean isLastVariableInDeclaration = (variableIndex + 1) == variableNames.size();

      printer.print(variableNames.get(variableIndex).toString());
      if (!isLastVariableInDeclaration) {
        printer.print(", ");
      }

    }

    printer.print(" ");
  }

  private void printDeclarationType(final ASTDeclaration astDeclaration) {
    printer.print(deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(astDeclaration.getDatatype())));
    if (astDeclaration.getSizeParameter().isPresent()) {
      printer.print(" [" + astDeclaration.getSizeParameter().get() + "]");
    }

  }

  private void printOptionalInitializationExpression(final ASTDeclaration astDeclaration) {
    if (astDeclaration.getExpr().isPresent()) {
      printer.print(" = " + expressionsPrinter.print(astDeclaration.getExpr().get()));
    }

  }

  /**
   * Small_Stmt = Assignment| FunctionCall | Declaration | ReturnStmt;
   */
  @Override
  public void handle(final ASTSmall_Stmt astSmallStmt ) {
    CommentPrettyPrinter.printPreComments(astSmallStmt, printer);

    if (astSmallStmt.getAssignment().isPresent()) {
      my_handle(astSmallStmt.getAssignment().get());
    } else if (astSmallStmt.getFunctionCall().isPresent()) {
      my_handle(astSmallStmt.getFunctionCall().get());
    }  else if (astSmallStmt.getDeclaration().isPresent()) {
      // TODO: must be also a functions that is get called from the corresponding method
      astSmallStmt.getDeclaration().get().accept(this);
    }  else if (astSmallStmt.getReturnStmt().isPresent()) {
      my_handle(astSmallStmt.getReturnStmt().get());
    }
    printer.println();
    CommentPrettyPrinter.printPreComments(astSmallStmt, printer);
  }

  /**
   * Grammar:
   * Assignment = variableName:QualifiedName "=" Expr;
   */
  public void my_handle(final ASTAssignment astAssignment) {
    final String lhsVariableName = astAssignment.getLhsVarialbe().toString();
    final String rhsOfAssignment = expressionsPrinter.print(astAssignment.getExpr());
    if (astAssignment.isAssignment()) {
      printer.print(lhsVariableName + " = " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundSum()) {
      printer.print(lhsVariableName + " += " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundMinus()) {
      printer.print(lhsVariableName + " -= " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundProduct()) {
      printer.print(lhsVariableName + " *= " + rhsOfAssignment);
    }
    if (astAssignment.isCompoundQuotient()) {
      printer.print(lhsVariableName + " /= " + rhsOfAssignment);
    }

  }

  /**
   * Grammar:
   * FunctionCall = QualifiedName "(" ArgList ")";
   * ArgList = (args:Expr ("," args:Expr)*)?;
   */

  public void my_handle(final ASTFunctionCall astFunctionCall) {
    final String functionName = astFunctionCall.getCalleeName();
    printer.print(functionName + "(");
    final List<ASTExpr> functionArguments = astFunctionCall.getArgs();
    for (int argumentIndex = 0; argumentIndex < functionArguments.size(); ++argumentIndex) {
      boolean isLastFunctionArgument = (argumentIndex + 1) == functionArguments.size();
      final ASTExpr currentArgument = functionArguments.get(argumentIndex);
      printer.print(expressionsPrinter.print(currentArgument));
      if (!isLastFunctionArgument) {
        printer.print(", ");
      }

    }
    printer.print(")");
  }

  /**
   * ReturnStmt = "return" Expr?;
   */
  public void my_handle(final ASTReturnStmt astReturnStmt) {

    if (astReturnStmt.getExpr().isPresent()) {
      final String returnExpressionAsString = expressionsPrinter.print(astReturnStmt.getExpr().get());
      printer.print("return " + returnExpressionAsString);
    }
    else {
      printer.print("return");
    }

  }
}
