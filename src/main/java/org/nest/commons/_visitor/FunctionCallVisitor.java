/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.commons._visitor;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.NestmlSymbols;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import java.util.List;
import java.util.Optional;

/**
 * Checks all function calls in an expression. For a not-void methods returns just its return type. For a void methods,
 * reports an error.
 *
 * @author plotnikov, ptraeder
 */
public class FunctionCallVisitor implements CommonsVisitor {
  final String ERROR_CODE = "SPL_FUNCTION_CALL_VISITOR";

  @Override
  public void visit(final ASTExpr expr) {
    final String functionName = expr.getFunctionCall().get().getCalleeName();

    final Optional<MethodSymbol> methodSymbol = NestmlSymbols.resolveMethod(expr.getFunctionCall().get());

    if (!methodSymbol.isPresent()) {
      final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +"Cannot resolve the method: " + functionName;
      expr.setType(Either.error(errorMsg));
      return;
    }

    //install conversions for parameter types if necessary
    boolean needUpdate = false;
    List<ASTExpr> fullParamList = expr.getFunctionCall().get().getArgs();
    for (int i=0; i < methodSymbol.get().getParameterTypes().size(); i++){
      TypeSymbol expectedParam = methodSymbol.get().getParameterTypes().get(i);
      TypeSymbol actualParam = expr.getFunctionCall().get().getArgs().get(i).getType().getValue(); //types in lower levels of AST already calculated
      if(!isCompatible(expectedParam,actualParam)){
        if(isUnit(expectedParam) && isUnit(actualParam)) {
          needUpdate = true;
          UnitRepresentation expectedTypeRep = UnitRepresentation.getBuilder().serialization(expectedParam.getName()).build();
          UnitRepresentation actualTypeRep = UnitRepresentation.getBuilder().serialization(actualParam.getName()).build();
          if(actualTypeRep.equalBase(expectedTypeRep)) {
            //Determine the difference in magnitude
            int magDiff = actualTypeRep.getMagnitude() - expectedTypeRep.getMagnitude();

            //replace actualParam expression with multiplication
            fullParamList.set(i,AstUtils.createSubstitution(fullParamList.get(i),magDiff));

            //drop warning about implicit conversion
            Log.warn(ERROR_CODE +" "+AstUtils.print(expr.get_SourcePositionStart()) + " : Implicit conversion from "+actualTypeRep.prettyPrint()+" to "+expectedTypeRep.prettyPrint());
          }
        }
      }
    }

    //set modified parameter list
    expr.getFunctionCall().get().setArgs(fullParamList);

    //revisit current sub-tree with substitution if a change happened
    if(needUpdate) {
      ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
      expr.accept(expressionTypeVisitor);
    }

    if (TypeChecker.isVoid(methodSymbol.get().getReturnType())) {
      final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +"Function " + functionName + " with the return-type 'Void'"
                              + " cannot be used in expressions. @" + expr.get_SourcePositionEnd();
      expr.setType(Either.error(errorMsg));
      return;
    }
    expr.setType(Either.value(methodSymbol.get().getReturnType()));
  }

}
