package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.spl._ast.ASTAssignment;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Computes how the setter call looks like
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 * @since TODO
 */
@SuppressWarnings("unused") // methods are called from templates
public class SPLVariableGetterSetterHelper {

  /**
   * Checks if the assignment
   */
  public boolean isLocal(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent());
    final Scope scope = astAssignment.getEnclosingScope().get();

    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> variableSymbol = scope.resolve(variableName, VariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the spl variable: " + variableName);

    // TODO does it make sense for the nestml?
    if (variableSymbol.get().getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
      return true;
    }
    else {
      return false;
    }

  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printVariableName(final ASTAssignment astAssignment) {
    return Names.getQualifiedName(astAssignment.getVariableName().getParts());
  }


  /**
   * Returns the textual representation of the setter invocation
   */
  public String printSetterName(final ASTAssignment astAssignment) {
    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    return "set_" + variableName;
  }

  /**
   * Returns the textual representation of the setter invocation
   */
  public String printGetterName(final ASTAssignment astAssignment) {
    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    return "get_" + variableName;
  }

  public boolean isVector(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent());
    final Scope scope = astAssignment.getEnclosingScope().get();

    final String variableName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> variableSymbol = scope.resolve(variableName, VariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the spl variable: " + variableName);


    if (variableSymbol.get().getArraySizeParameter().isPresent()) {
      return true;
    }
    // TODO to complex logic, refactor
    final Optional<String> arrayVariable = ASTNodes.getVariablesNamesFromAst(astAssignment.getExpr())
        .stream()
        .filter(
            variableNameInExpression -> {
              final Optional<VariableSymbol> variableSymbolExpr = scope
                  .resolve(variableNameInExpression, VariableSymbol.KIND);
              checkState(variableSymbolExpr.isPresent(),
                  "Cannot resolve the spl variable: " + variableNameInExpression);
              if (variableSymbolExpr.get().getArraySizeParameter().isPresent()) {
                return true;
              }
              else {
                return false;
              }
            }
        ).findFirst();

    return arrayVariable.isPresent();
  }

}
