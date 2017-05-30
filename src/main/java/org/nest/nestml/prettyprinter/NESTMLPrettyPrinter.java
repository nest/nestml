/*
* Copyright (c) 2015 RWTH Aachen. All rights reserved.
*
* http://www.se-rwth.de/
*/
package org.nest.nestml.prettyprinter;

import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.utils.AstUtils;
import org.nest.utils.PrettyPrinterBase;

import java.util.List;
import java.util.Optional;

import static org.nest.nestml.prettyprinter.SPLPrettyPrinterFactory.createDefaultPrettyPrinter;
import static org.nest.symboltable.typechecking.TypeChecker.deserializeUnitIfNotPrimitive;
import static org.nest.utils.AstUtils.printComments;

/**
 * Provides convenient  functions to statically type interfaces astnodes resulting from the Body-grammar
 * production.
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 */
public class NESTMLPrettyPrinter extends PrettyPrinterBase implements NESTMLInheritanceVisitor {
  private final ExpressionsPrettyPrinter expressionsPrinter;

  public static class Builder {
    public static NESTMLPrettyPrinter build() {
      return new NESTMLPrettyPrinter(new ExpressionsPrettyPrinter());
    }
  }

  private NESTMLPrettyPrinter(final ExpressionsPrettyPrinter expressionsPrinter) {
    this.expressionsPrinter = expressionsPrinter;
  }

  /**
   *   NESTMLCompilationUnit = "package" packageName:QualifiedName
   *   BLOCK_OPEN
   *   (Import | NEWLINE)*
   *   (Neuron | Component | SL_COMMENT | NEWLINE)*
   *   BLOCK_CLOSE (SL_COMMENT | NEWLINE)*;
   */
  @Override
  public void visit(final ASTNESTMLCompilationUnit node) {
    printCommentsIfPresent(node);
  }


  /**
   * Grammar:
   * Neuron = "neuron" Name Body;
   */
  @Override
  public void visit(final ASTNeuron astNeuron) {
    printCommentsIfPresent(astNeuron);

    print("neuron " + astNeuron.getName());
  }

  /**
   * Grammar:
   * Body = BLOCK_OPEN ( SL_COMMENT | NEWLINE | BodyElement)* BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTBody astBody) {
    printCommentsIfPresent(astBody);
    println(BLOCK_OPEN);
    indent();
  }

  /**
   * Grammar:
   * Body = BLOCK_OPEN ( SL_COMMENT | NEWLINE | BodyElement)* BLOCK_CLOSE;
   */
  @Override
  public void endVisit(final ASTBody astBody) {
    unindent();
    println(BLOCK_CLOSE);
  }

  @Override
  public void visit(final ASTBodyElement astBodyElement) {
    printCommentsIfPresent(astBodyElement);
  }
  /**
   * Var_Block implements BodyElement =
   * ([state:"state"]|[para:"parameter"]|[internal:"internal"])
   *  BLOCK_OPEN
   *     (AliasDecl (";" AliasDecl)* (";")?
   *     | SL_COMMENT | NEWLINE)*
   *  BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTVar_Block astVarBlock) {
    printBlockKeyword(astVarBlock);
    indent();
  }

  private void printBlockKeyword(final ASTVar_Block astVarBlock) {
    if (astVarBlock.isState()) {
      println("state" + BLOCK_OPEN);
    }
    else if (astVarBlock.isInternals()) {
      println("internals" + BLOCK_OPEN);
    }
    else if (astVarBlock.isParameters ()) {
      println("parameters" + BLOCK_OPEN);
    }
    for (ASTDeclaration astDeclaration:astVarBlock.getDeclarations()) {
      printDeclarationStatement(astDeclaration);
      println();
    }

  }

  private void printDeclarationStatement(final ASTDeclaration astDeclaration) {
    final SPLPrettyPrinter splPrettyPrinter = createDefaultPrettyPrinter(getIndentionLevel());
    splPrettyPrinter.printDeclaration(astDeclaration);
    print(splPrettyPrinter.result());
  }


  @Override
  public void endVisit(final ASTVar_Block astVarBlock) {
    unindent();
    println(BLOCK_CLOSE);
  }

  /**
   * Grammar:
   * Input implements BodyElement = "input"
   * BLOCK_OPEN
   *   (InputLine | SL_COMMENT | NEWLINE)*
   * BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTInput astInput) {
    println("input" + BLOCK_OPEN);
    indent();
  }

  /**
   * Grammar:
   * Input implements BodyElement = "input"
   * BLOCK_OPEN
   *   (InputLine | SL_COMMENT | NEWLINE)*
   * BLOCK_CLOSE;
   */
  @Override
  public void endVisit(final ASTInput astInput) {
    unindent();
    println(BLOCK_CLOSE);
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
  public void visit(final ASTOdeDeclaration astOdeDeclaration) {
    println("equations" + BLOCK_OPEN);
    indent();

    astOdeDeclaration.getShapes().forEach(this::printShape);
    astOdeDeclaration.getOdeFunctions().forEach(this::printODEAlias);
    astOdeDeclaration.getODEs().forEach(this::printEquation);

  }

  private void printEquation(final ASTEquation astEquation) {
    println(astEquation.getLhs() + " = " + expressionsPrinter.print(astEquation.getRhs()));
  }

  /**
   * This method is used in freemaker template. Therefore, remains public.
   */
  public void printShape(final ASTShape astShape) {
    println("shape " + astShape.getLhs() + " = " + expressionsPrinter.print(astShape.getRhs()));
  }

  /**
   * This method is used in freemaker template. Therefore, remains public.
   */
  public void printODEAlias(final ASTOdeFunction astOdeAlias) {
    final String datatype = deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(astOdeAlias.getDatatype()));
    final String initExpression = expressionsPrinter.print(astOdeAlias.getExpr());
    if (astOdeAlias.isRecordable()) {
      print("recordable ");
    }
    println("function " + astOdeAlias.getVariableName() + " " + datatype + " = " + initExpression);
  }

  @Override
  public void endVisit(final ASTEquations astEquations) {
    unindent();
    println(BLOCK_CLOSE);
  }

  /**
   * grammar
   * InputLine = Name "<-" InputType* ([spike:"spike"]|[current:"current"]);
   * InputType = (["inhibitory"]|["excitatory"]);
   */
  @Override
  public void visit(final ASTInputLine astInputLine) {
    print(astInputLine.getName());
    printArrayParameter(astInputLine);
    print(" <- ");
    printInputTypes(astInputLine.getInputTypes());
    printOutputType(astInputLine);
    println();
  }

  private void printInputTypes(final List<ASTInputType> inputTypes) {
    for (final ASTInputType inputType:inputTypes) {
      if (inputType.isInhibitory()) {
        print("inhibitory ");
      }
      else {
        print("excitatory ");
      }

    }

  }

  private void printArrayParameter(final ASTInputLine astInputLine) {
    astInputLine.getSizeParameter().ifPresent(parameter -> print("[" + parameter + "]"));
  }

  private void printOutputType(final ASTInputLine astInputLine) {
    if (astInputLine.isSpike()) {
      print("spike");
    }
    else {
      print("current");
    }

  }

  /**
   * Output implements BodyElement =
   * "output" BLOCK_OPEN ([spike:"spike"]|[current:"current"]) ;
   */
  @Override
  public void visit(final ASTOutput astOutput) {
    print("output: ");
    if (astOutput.isSpike()) {
      print("spike");
    }
    else {
      print("current");
    }

    println();
  }

  /**
   * Function implements BodyElement =
     "function" Name "(" Parameters? ")" (returnType:QualifiedName | PrimitiveType)?
     BLOCK_OPEN
       Block
     BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTFunction astFunction) {
    print("function " + astFunction.getName());
    printParameters(astFunction.getParameters());
    printOptionalReturnValue(astFunction);
    println(BLOCK_OPEN);
    indent();
    printSplBlock(astFunction.getBlock());
    unindent();
    println(BLOCK_CLOSE);

  }

  private void printParameters(final Optional<ASTParameters> functionParameters) {
    print("(");
    if (functionParameters.isPresent()) {
      final List<ASTParameter> astParameters = functionParameters.get().getParameters();
      for (int curParameterIndex = 0; curParameterIndex < astParameters.size(); ++curParameterIndex) {
        boolean isLastParameter = (curParameterIndex + 1) == astParameters.size();
        final ASTParameter curParameter = astParameters.get(curParameterIndex);
        print(curParameter.getName() + " " + deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(curParameter.getDatatype())));
        if (!isLastParameter) {
          print(", ");
        }

      }

    }
    print(")");
  }

  private void printOptionalReturnValue(final ASTFunction astFunction) {
    if (astFunction.getReturnType().isPresent()) {
      print(deserializeUnitIfNotPrimitive(AstUtils.computeTypeName(astFunction.getReturnType().get())));
    }

  }


  private void printSplBlock(final ASTBlock astBlock) {
    final  SPLPrettyPrinter splPrinter = createDefaultPrettyPrinter(getIndentionLevel());
    splPrinter.print(astBlock);

    print(splPrinter.result());
  }

  /**
   * Dynamics implements BodyElement =
   * "update:"
   *   BLOCK_OPEN
   *     Block
   *   BLOCK_CLOSE;
   */
  @Override
  public void visit(final ASTDynamics astDynamics) {
    print("update");
    println(BLOCK_OPEN);
    indent();
    printSplBlock(astDynamics.getBlock());
    unindent();
    println();
    println(BLOCK_CLOSE);
  }

  private void printCommentsIfPresent(final ASTNESTMLNode astNestmlNode) {
    final String comment = printComments(astNestmlNode);
    if (!comment.isEmpty()) {
      println(comment);
    }

  }

}
