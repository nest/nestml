package org.nest.commons._visitor;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTVariable;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.NESTMLSymbols;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;
import static org.nest.utils.AstUtils.getNameOfLHS;

import java.util.Optional;

/**
 * @author ptraeder
 */
public class VariableVisitor implements CommonsVisitor{
  final String ERROR_CODE = "NESTML_VARIABLE_VISITOR: ";
  @Override
  public void visit(ASTExpr expr) {
    final Scope scope = expr.getEnclosingScope().get();
    final ASTVariable varNode = expr.getVariable().get(); //guaranteed to exist if this visitor is called
    final String varName = expr.getVariable().get().toString();
    final Optional<VariableSymbol> var = scope.resolve(varName, VariableSymbol.KIND);

    if (var.isPresent()) {
    /*  if(varNode.getDifferentialOrder().size() !=0 && var.get().getType().getType() == TypeSymbol.Type.UNIT){
        UnitRepresentation deriveMe = new UnitRepresentation(var.get().getType().getName());
        deriveMe = deriveMe.deriveT(varNode.getDifferentialOrder().size());
        TypeSymbol derivedType = getType(deriveMe.serialize());
        expr.setType(Either.value(derivedType));
      }
      else{*/
        expr.setType(Either.value(var.get().getType()));
      //}
    }
    else {
      final String errorMsg = ERROR_CODE+"ExpressionCalculator cannot resolve the variable: " + varName;
      expr.setType(Either.error(errorMsg));
      error(errorMsg,expr.get_SourcePositionStart());
    }
  }
}
