package org.nest.spl.cocos;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.*;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl._cocos.SPLASTFOR_StmtCoCo;
import org.nest.spl._cocos.SPLASTOdeDeclarationCoCo;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.Names.getQualifiedName;
import static de.se_rwth.commons.logging.Log.error;
import static java.util.stream.Collectors.toList;

public class VariableNotDefinedBeforeUse implements
    SPLASTAssignmentCoCo,
    SPLASTDeclarationCoCo,
    SPLASTFOR_StmtCoCo {

  public static final String ERROR_CODE = "SPL_VARIABLE_NOT_DEFINED_BEFORE_USE";
  private static final String ERROR_MSG_FORMAT = "Variable '%s' not defined yet. It is defined at line '%d'";

  @Override
  public void check(final ASTFOR_Stmt forstmt) {
    String fullName = forstmt.getVar();
    check(fullName, forstmt);
  }

  @Override
  public void check(final ASTAssignment assignment) {
      String fullName = getQualifiedName(assignment.getVariableName().getParts());
      check(fullName, assignment);
  }

  @Override
  public void check(final ASTDeclaration decl) {
    if (decl.getExpr().isPresent()) {
      final List<String> varsOfCurrentDecl = Lists.newArrayList(decl.getVars());
      final List<ASTQualifiedName> variablesNamesRHS = getVariablesFromExpressions(decl.getExpr().get());
      // check, if variable of the left side is used in the right side, e.g. in decl-vars

      for (final ASTQualifiedName variableName: variablesNamesRHS) {
        final String varRHS = getQualifiedName(variableName.getParts());
        final Optional<VariableSymbol> variableSymbol = decl.getEnclosingScope().get().resolve(
            varRHS, VariableSymbol.KIND);
        checkState(variableSymbol.isPresent(), "Cannot resolve the symbol:  "+varRHS);
        // e.g. x real = 2 * x
        if (varsOfCurrentDecl.contains(varRHS)) {
          final String logMsg = "Cannot use variable '%s' in the assignment of its own declaration.";
          error(ERROR_CODE + ":" + String.format(logMsg, varRHS),
              decl.get_SourcePositionStart());
        }
        else if (variableName.get_SourcePositionStart().compareTo(variableSymbol.get().getAstNode().get().get_SourcePositionStart()) < 0) {
          // y real = 5 * x
          // x integer = 1
          final String logMsg = "Cannot use variable '%s' before its usage.";
          error(ERROR_CODE + ":" + String.format(logMsg, getQualifiedName(variableName.getParts())),
              decl.get_SourcePositionStart());
        }

      }

    }

  }

  protected List<ASTQualifiedName> getVariablesFromExpressions(final  ASTExpr expression) {
    final List<ASTQualifiedName> names = ASTNodes
        .getSuccessors(expression, ASTQualifiedName.class);

    final List<String> functions = ASTNodes
        .getSuccessors(expression, ASTFunctionCall.class).stream()
        .map(astFunctionCall -> Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts()))
        .collect(Collectors.toList());

    return names.stream()
        .filter(name -> !functions.contains(Names.getQualifiedName(name.getParts())))
        .collect(toList());
  }

  protected void check(final String varName, final ASTNode node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = node.getEnclosingScope().get();

    Optional<VariableSymbol> varOptional = scope.resolve(varName, VariableSymbol.KIND);

    if(varOptional.isPresent()) {
      // exists
      if (node.get_SourcePositionStart().compareTo(varOptional.get().getSourcePosition()) < 0) {
        Log.error(ERROR_CODE + ":" +
                String
                    .format(ERROR_MSG_FORMAT, varName, varOptional.get().getSourcePosition().getLine()),
            node.get_SourcePositionEnd());
      }
    }
    else {
      Log.warn(ERROR_CODE +  "Variable " + varName + " couldn't be resolved.");
    }

  }

}
