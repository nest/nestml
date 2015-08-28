package org.nest.spl.cocos;

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTFOR_Stmt;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl._cocos.SPLASTFOR_StmtCoCo;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.Names.getQualifiedName;
import static de.se_rwth.commons.logging.Log.error;

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
      final List<ASTQualifiedName> variablesNamesRHS = ASTNodes.getSuccessors(decl.getExpr().get(), ASTQualifiedName.class);

      // check, if variable of the left side is used in the right side, e.g. in decl-vars
      // e.g. x real = 2 * x
      for (ASTQualifiedName variableName: variablesNamesRHS) {
        final String varRHS = getQualifiedName(variableName.getParts());
        if (varsOfCurrentDecl.contains(varRHS)) {
          final String logMsg = "Cannot use variable '%s' in the assignment of its own declaration.";
          error(ERROR_CODE + ":" + String.format(logMsg, varRHS),
              decl.get_SourcePositionStart());
        }
        else if (variableName.get_SourcePositionStart().compareTo(decl.get_SourcePositionStart()) > 0) {
          // y real = 5 * x
          // x integer = 1
          final String logMsg = "Cannot use variable '%s' before its usage.";
          error(ERROR_CODE + ":" + String.format(logMsg, getQualifiedName(variableName.getParts())),
              decl.get_SourcePositionStart());
        }

      }

    }

  }

  protected void check(final String varName, final ASTNode node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = node.getEnclosingScope().get();

    Optional<NESTMLVariableSymbol> varOptional = scope.resolve(varName, NESTMLVariableSymbol.KIND);
    Preconditions.checkState(varOptional.isPresent(), "Variable " + varName + " couldn't be resolved.");
    // exists
    if (node.get_SourcePositionStart().compareTo(varOptional.get().getSourcePosition()) < 0) {
      Log.error(ERROR_CODE + ":" +
          String.format(ERROR_MSG_FORMAT, varName, varOptional.get().getSourcePosition().getLine()),
          node.get_SourcePositionEnd());
    }

  }

}
