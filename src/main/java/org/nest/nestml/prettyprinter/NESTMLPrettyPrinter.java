/*
* Copyright (c) 2015 RWTH Aachen. All rights reserved.
*
* http://www.se-rwth.de/
*/
package org.nest.nestml.prettyprinter;

import de.monticore.prettyprint.CommentPrettyPrinter;
import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.utils.AstUtils;

import java.util.List;
import java.util.Optional;

import static org.nest.nestml._symboltable.typechecking.TypeChecker.deserializeUnitIfNotPrimitive;

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
  private final IndentPrinter printer = new IndentPrinter();

  private NESTMLPrettyPrinter() {
    this.expressionsPrinter = new ExpressionsPrettyPrinter();
  }

  public static String print(final ASTNESTMLNode astNestmlNode) {
    final NESTMLPrettyPrinter prettyPrinter = new NESTMLPrettyPrinter();
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
   */
  @Override
  public void handle(final ASTNeuron astNeuron) {
    CommentPrettyPrinter.printPreComments(astNeuron, printer);

    printer.println("neuron " + astNeuron.getName() + BLOCK_OPEN);
    printer.indent();

    printNodes(astNeuron.getBlockWithVariabless());
    printNodes(astNeuron.getUpdateBlocks());
    printNodes(astNeuron.getEquationsBlocks());
    printNodes(astNeuron.getInputBlocks());
    printNodes(astNeuron.getOutputBlocks());
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
    else if (astVarBlock.isInitial_values ()) {
      printer.println("initial_values" + BLOCK_OPEN);
    }

  }

  public void handle(final ASTUpdateBlock astUpdateBlock) {
    CommentPrettyPrinter.printPreComments(astUpdateBlock, printer);
    printer.println("update" + BLOCK_OPEN);
    printer.indent();

    printNode(astUpdateBlock.getBlock());

    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPostComments(astUpdateBlock, printer);
  }

  @Override
  public void handle(final ASTInputBlock astInput) {
    CommentPrettyPrinter.printPreComments(astInput, printer);
    printer.println("input" + BLOCK_OPEN);
    printer.indent();

    for (final ASTInputLine astInputLine:astInput.getInputLines()) {
      printer.print(astInputLine.getName());
      printArrayParameter(astInputLine);
      printer.print(" <- ");
      printInputTypes(astInputLine.getInputTypes());
      printOutputType(astInputLine);
      printer.println();
    }

    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPreComments(astInput, printer);

  }

  private void printInputTypes(final List<ASTInputType> inputTypes) {
    for (final ASTInputType inputType:inputTypes) {
      if (inputType.isInhibitory()) {
        printer.print("inhibitory ");
      }
      else {
        printer.print("excitatory ");
      }

    }

  }

  private void printArrayParameter(final ASTInputLine astInputLine) {
    astInputLine.getSizeParameter().ifPresent(parameter -> printer.print("[" + parameter + "]"));
  }

  private void printOutputType(final ASTInputLine astInputLine) {
    if (astInputLine.isSpike()) {
      printer.print("spike");
    }
    else {
      printer.print("current");
    }

  }
  @Override
  public void handle(final ASTFunction astFunction) {
    CommentPrettyPrinter.printPreComments(astFunction, printer);
    printer.print("function " + astFunction.getName());
    printParameters(astFunction.getParameters());
    printOptionalReturnValue(astFunction);
    printer.println(BLOCK_OPEN);
    printer.indent();
    astFunction.getBlock().accept(this);
    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPostComments(astFunction, printer);
  }


  private void printParameters(final List<ASTParameter> astParameters) {
    printer.print("(");
    for (int curParameterIndex = 0; curParameterIndex < astParameters.size(); ++curParameterIndex) {
      boolean isLastParameter = (curParameterIndex + 1) == astParameters.size();
      final ASTParameter curParameter = astParameters.get(curParameterIndex);
      printer.print(curParameter.getName() + " " + deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(curParameter.getDatatype())));
      if (!isLastParameter) {
        printer.print(", ");
      }

    }

    printer.print(")");
  }

  private void printOptionalReturnValue(final ASTFunction astFunction) {
    if (astFunction.getReturnType().isPresent()) {
      printer.print(deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(astFunction.getReturnType().get())));
    }

  }

  @Override
  public void handle(final ASTOutputBlock astOutput) {
    printer.print("output: ");
    if (astOutput.isSpike()) {
      printer.print("spike");
    }
    else {
      printer.print("current");
    }

    printer.println();
  }
  /**
   * Equations implements BodyElement =
   * "equations"
   * BLOCK_OPEN
   *   OdeDeclaration
   * BLOCK_CLOSE;
   *
   * OdeDeclaration  = (Eq | Shape | ODEAlias | NEWLINE)+;
   * Equation = lhs:Derivative "=" rhs:Expr (";")?;
   * Derivative = name:QualifiedName (differentialOrder:"\'")*;
   * ODEAlias = variableName:Name Datatype "=" Expr;
   */
  @Override
  public void handle(final ASTEquationsBlock astOdeDeclaration) {
    CommentPrettyPrinter.printPreComments(astOdeDeclaration, printer);
    printer.println("equations" + BLOCK_OPEN);
    printer.indent();

    astOdeDeclaration.getShapes().forEach(astShape -> printShape(astShape, printer));
    astOdeDeclaration.getOdeFunctions().forEach(astOdeFunction -> printOdeFunctions(astOdeFunction, printer));
    astOdeDeclaration.getEquations().forEach(astEquation -> printEquation(astEquation, printer));

    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPreComments(astOdeDeclaration, printer);
  }


  private void printShape(final ASTShape shape, final IndentPrinter printer) {
    CommentPrettyPrinter.printPreComments(shape, printer);
    printer.println(printShape(shape));
    CommentPrettyPrinter.printPostComments(shape, printer);
  }

  /**
   * This method is used in freemarker template. Therefore, it must remain public.
   */
  public String printShape(final ASTShape astShape) {
    return "shape " + astShape.getLhs() + " = " + expressionsPrinter.print(astShape.getRhs());
  }

  private void printOdeFunctions(final ASTOdeFunction astOdeFunction, final IndentPrinter printer) {
    CommentPrettyPrinter.printPreComments(astOdeFunction, printer);
    printer.println(printOdeFunction(astOdeFunction));
    CommentPrettyPrinter.printPostComments(astOdeFunction, printer);
  }

  /**
   * This method is used in freemaker template. Therefore, remains public.
   */
  public String printOdeFunction(final ASTOdeFunction astOdeFunction) {

    final String datatype = deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(astOdeFunction.getDatatype()));

    final String initExpression = expressionsPrinter.print(astOdeFunction.getExpr());
    final StringBuilder recordable = new StringBuilder();
    if (astOdeFunction.isRecordable()) {
      recordable.append("recordable ");
    }
    return recordable.toString() + "function " + astOdeFunction.getVariableName() + " " + datatype + " = " + initExpression;
  }

  private void printEquation(final ASTEquation astEquation, final IndentPrinter printer) {
    CommentPrettyPrinter.printPreComments(astEquation, printer);
    printer.println(printEquation(astEquation));
    CommentPrettyPrinter.printPostComments(astEquation, printer);
  }

  /**
   * This method is used in freemaker template. Therefore, it must remain public.
   */
  public String printEquation(final ASTEquation astEquation) {
    return astEquation.getLhs() + " = " + expressionsPrinter.print(astEquation.getRhs());
  }
  ////////////////////////////////////////////////////////////////////////////
  // SPL PART
  ////////////////////////////////////////////////////////////////////////////
  public void handle(final ASTStmt astStmt) {
    CommentPrettyPrinter.printPreComments(astStmt, printer);
    if (astStmt.small_StmtIsPresent()) {
      printNode(astStmt.getSmall_Stmt().get());
    }
    else if (astStmt.compound_StmtIsPresent()) {
      printNode(astStmt.getCompound_Stmt().get());
    }

    CommentPrettyPrinter.printPostComments(astStmt, printer);
  }

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
  public void handle(final ASTSmall_Stmt astSmallStmt) {
    CommentPrettyPrinter.printPreComments(astSmallStmt, printer);

    if (astSmallStmt.getAssignment().isPresent()) {
      printAssignment(astSmallStmt.getAssignment().get());
    } else if (astSmallStmt.getFunctionCall().isPresent()) {
      printFunctionCall(astSmallStmt.getFunctionCall().get());
    }  else if (astSmallStmt.getDeclaration().isPresent()) {
      // TODO: must be also a functions that is get called from the corresponding method
      astSmallStmt.getDeclaration().get().accept(this);
    }  else if (astSmallStmt.getReturnStmt().isPresent()) {
      printReturnStatement(astSmallStmt.getReturnStmt().get());
    }
    printer.println();
    CommentPrettyPrinter.printPreComments(astSmallStmt, printer);
  }

  /**
   * Grammar:
   * Assignment = variableName:QualifiedName "=" Expr;
   */
  private void printAssignment(final ASTAssignment astAssignment) {
    CommentPrettyPrinter.printPreComments(astAssignment, printer);
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
    CommentPrettyPrinter.printPostComments(astAssignment, printer);
  }

  /**
   * Grammar:
   * FunctionCall = QualifiedName "(" ArgList ")";
   * ArgList = (args:Expr ("," args:Expr)*)?;
   */

  private void printFunctionCall(final ASTFunctionCall astFunctionCall) {
    CommentPrettyPrinter.printPreComments(astFunctionCall, printer);
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
    CommentPrettyPrinter.printPostComments(astFunctionCall, printer);
  }

  /**
   * ReturnStmt = "return" Expr?;
   */
  private void printReturnStatement(final ASTReturnStmt astReturnStmt) {
    CommentPrettyPrinter.printPreComments(astReturnStmt, printer);
    if (astReturnStmt.getExpr().isPresent()) {
      final String returnExpressionAsString = expressionsPrinter.print(astReturnStmt.getExpr().get());
      printer.print("return " + returnExpressionAsString);
    }
    else {
      printer.print("return");
    }
    CommentPrettyPrinter.printPostComments(astReturnStmt, printer);
  }

  @Override
  public void handle(final ASTCompound_Stmt astCompoundStmt) {
    CommentPrettyPrinter.printPreComments(astCompoundStmt, printer);

    if (astCompoundStmt.getIF_Stmt().isPresent()) {
      final ASTIF_Stmt ifStatement = astCompoundStmt.getIF_Stmt().get();
      printIfStatement(ifStatement);
    }
    else if (astCompoundStmt.getFOR_Stmt().isPresent()) {
      final ASTFOR_Stmt astForStmt = astCompoundStmt.getFOR_Stmt().get();
      printForStatement(astForStmt);
    }
    else if (astCompoundStmt.getWHILE_Stmt().isPresent()) {
      final ASTWHILE_Stmt astWhileStatement = astCompoundStmt.getWHILE_Stmt().get();
      printWhileStatement(astWhileStatement);
    }

    CommentPrettyPrinter.printPostComments(astCompoundStmt, printer);
  }

  private void printWhileStatement(ASTWHILE_Stmt astWhileStatement) {
    CommentPrettyPrinter.printPreComments(astWhileStatement, printer);
    printer.print("while ");
    printer.print(expressionsPrinter.print(astWhileStatement.getExpr()));
    printer.println(BLOCK_OPEN);
    printer.indent();
    printNode(astWhileStatement.getBlock());
    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPostComments(astWhileStatement, printer);
  }

  private void printForStatement(ASTFOR_Stmt astForStmt) {
    CommentPrettyPrinter.printPreComments(astForStmt, printer);
    printer.print("for ");
    printer.print(astForStmt.getVar());
    printer.print(" in ");
    printer.print(expressionsPrinter.print(astForStmt.getFrom()));
    printer.print(" ... ");
    printer.print(expressionsPrinter.print(astForStmt.getTo()));
    printer.print(" step ");
    printer.print(typesPrinter().prettyprint(astForStmt.getStep()));

    printer.println(BLOCK_OPEN);
    printer.indent();
    printNode(astForStmt.getBlock());
    printer.unindent();
    printer.println(BLOCK_CLOSE);
    CommentPrettyPrinter.printPostComments(astForStmt, printer);
  }

  private void printIfStatement(ASTIF_Stmt ifStatement) {
    CommentPrettyPrinter.printPreComments(ifStatement, printer);
    final String ifCondition = expressionsPrinter.print(ifStatement.getIF_Clause().getExpr());

    CommentPrettyPrinter.printPreComments(ifStatement.getIF_Clause(), printer);
    CommentPrettyPrinter.printPostComments(ifStatement.getIF_Clause(), printer);
    printer.println("if " + ifCondition + BLOCK_OPEN);
    printer.indent();
    printNode(ifStatement.getIF_Clause().getBlock());
    printer.unindent();

    if (!ifStatement.getELSE_Clause().isPresent() &&
        ifStatement.getELIF_Clauses().isEmpty()) {
      printer.println(BLOCK_CLOSE);
    }

    for (final ASTELIF_Clause astElifClause:ifStatement.getELIF_Clauses()) {
      CommentPrettyPrinter.printPreComments(astElifClause, printer);
      CommentPrettyPrinter.printPostComments(astElifClause, printer);
      final String elifCondition = expressionsPrinter.print(astElifClause.getExpr());
      printer.println("elif " + elifCondition + BLOCK_OPEN);
      printer.indent();
      printNode(astElifClause.getBlock());
      printer.unindent();
    }
    if (!ifStatement.getELSE_Clause().isPresent() &&
        !ifStatement.getELIF_Clauses().isEmpty()) {
      printer.println(BLOCK_CLOSE);
    }

    if (ifStatement.getELSE_Clause().isPresent()) {
      final ASTELSE_Clause elseClause = ifStatement.getELSE_Clause().get();
      CommentPrettyPrinter.printPreComments(elseClause, printer);
      CommentPrettyPrinter.printPostComments(elseClause, printer);
      printer.println("else " + BLOCK_OPEN);
      printer.indent();
      printNode(elseClause.getBlock());
      printer.unindent();
      printer.println(BLOCK_CLOSE);
    }
    CommentPrettyPrinter.printPostComments(ifStatement, printer);
  }

  private TypesPrettyPrinterConcreteVisitor typesPrinter() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }

  private void printNodes(final List<? extends ASTNESTMLNode> nodes) {
    for (ASTNESTMLNode node:nodes) {
      printNode(node);
    }
  }

  private void printNode(ASTNESTMLNode node) {
    node.accept(this);
  }

}
