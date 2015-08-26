package org.nest.nestml.cocos;

import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTExpr;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

public class MemberVariablesInitialisedInCorrectOrder implements NESTMLASTAliasDeclCoCo {

  public static final String ERROR_CODE = "NESTML_MEMBER_VARIABLES_INITIALISED_IN_CORRECT_ORDER";

  /**
   * AliasDecl = ([hide:"-"])? ([alias:"alias"])? Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
   * Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
   *
   * @param alias
   */
  public void check(final ASTAliasDecl alias) {
    final Optional<? extends Scope> enclosingScope = alias.getEnclosingScope();
    checkState(enclosingScope.isPresent(),
        "There is no scope assigned to the AST node: " + alias);
    ASTDeclaration declaration = alias.getDeclaration();

    if (declaration.getExpr().isPresent() && declaration.getVars().size() > 0) {
      final String lhsVariableName = declaration.getVars().get(0); // has at least one declaration

      final Optional<NESTMLVariableSymbol> lhsSymbol = enclosingScope.get().resolve(
          lhsVariableName,
          NESTMLVariableSymbol.KIND); // TODO use cached version

      checkState(lhsSymbol.isPresent(), "Variable '" + lhsVariableName + "' is not defined");

      final List<ASTQualifiedName> variablesNames
          = ASTNodes.getSuccessors(declaration.getExpr().get(), ASTQualifiedName.class);

      for (ASTQualifiedName variableFqnAst : variablesNames) {
        final String rhsVariableName = Names.getQualifiedName(variableFqnAst.getParts());
        Optional<NESTMLVariableSymbol> rhsSymbol = enclosingScope.get().resolve(
            rhsVariableName,
            NESTMLVariableSymbol.KIND);

        if (!rhsSymbol.isPresent()) { // actually redudant and it is should be checked through another CoCo
          final String msg = "Variable '" + rhsVariableName + "' is undefined." + "<" +
              variableFqnAst.get_SourcePositionStart() + "," + variableFqnAst.get_SourcePositionEnd()  + ">";
          Log.warn(msg);
          return;
        }
        else  { //
          // not local, e.g. a variable in one of the blocks: state, parameter, or internal
          // both of same decl type
          checkIfDefinedInCorrectOrder(lhsSymbol.get(), rhsSymbol.get());

        }

      }

      for (ASTExpr aliasExpression:alias.getInvariants()) {
        final List<ASTQualifiedName> namesInInvariant
            = ASTNodes.getSuccessors(aliasExpression, ASTQualifiedName.class);

        for (ASTQualifiedName variableFqnAst : namesInInvariant) {
          final String rhsVariableName = Names.getQualifiedName(variableFqnAst.getParts());
          Optional<NESTMLVariableSymbol> variableSymbol = enclosingScope.get().resolve(
              rhsVariableName,
              NESTMLVariableSymbol.KIND);

          if (!variableSymbol.isPresent()) { // actually redudant and it is should be checked through another CoCo
            final String msg = "Variable '" + rhsVariableName + "' is undefined." + "<" +
                variableFqnAst.get_SourcePositionStart() + "," + variableFqnAst.get_SourcePositionEnd()  + ">";
            Log.warn(msg);
            return;
          }
          else  { //
            // not local, e.g. a variable in one of the blocks: state, parameter, or internal
            // both of same decl type
            checkIfDefinedInCorrectOrder(lhsSymbol.get(), variableSymbol.get());

          }

        }

      }

    }

  }

  protected void checkIfDefinedInCorrectOrder(
      final NESTMLVariableSymbol lhsSymbol,
      final NESTMLVariableSymbol rhsSymbol) {
    if (rhsSymbol.getDeclaringType().getName()
        .equals(lhsSymbol.getDeclaringType().getName())) {
      // same var - block? => used must be in
      // previous line
      if (rhsSymbol.getBlockType() == lhsSymbol.getBlockType()) {
        // same block not parameter block
        if (rhsSymbol.getSourcePosition().getLine() >
            lhsSymbol.getSourcePosition().getLine()) {
          final String msg = "Variable '"
              + rhsSymbol.getName()
              + "' must be declared before it can be used in declaration of '"
              + lhsSymbol.getName() + "'.";
          CoCoLog.error(ERROR_CODE, msg, rhsSymbol.getSourcePosition());

        }
      }
      if (rhsSymbol.getBlockType() != lhsSymbol.getBlockType() &&
          rhsSymbol.getBlockType() != NESTMLVariableSymbol.BlockType.PARAMETER) {
        final String msg = "Variable '"
            + rhsSymbol.getName()
            + "' must be declared in the parameter block to be used at this place. '"
            + lhsSymbol.getName() + "'.";
        CoCoLog.error(ERROR_CODE, msg, rhsSymbol.getSourcePosition());
      }

    }

  }



}
