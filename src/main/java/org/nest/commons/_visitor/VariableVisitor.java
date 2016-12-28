package org.nest.commons._visitor;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTVariable;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;

/**
 * @author ptraeder
 */
public class VariableVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_VARIABLE_VISITOR";
  @Override
  public void visit(ASTExpr expr) {
    final Scope scope = expr.getEnclosingScope().get();
    final ASTVariable varNode = expr.getVariable().get(); //guaranteed to exist if this visitor is called
    final String varName = expr.getVariable().get().toString();
    final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

    if (var.isPresent()) {
      if(var.get().isCurrentBuffer()){
        expr.setType(Either.value(getType("pA")));
      }else if(var.get().isSpikeBuffer()){
        expr.setType(Either.value(getRealType()));
      }else {
        expr.setType(Either.value(var.get().getType()));
      }
    }
    else {
      final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
          "ExpressionCalculator cannot resolve the variable: " + varName;
      expr.setType(Either.error(errorMsg));
      error(errorMsg,expr.get_SourcePositionStart());
    }
  }
}
