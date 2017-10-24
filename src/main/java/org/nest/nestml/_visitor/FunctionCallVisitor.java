/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._visitor;

import de.se_rwth.commons.logging.Log;
import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._cocos.SplErrorStrings;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.nestml._symboltable.NESTMLSymbolTableCreator;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.typechecking.TypeChecker;
import org.nest.nestml._symboltable.NestmlSymbols;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.isUnit;

/**
 * Checks all function calls in an expression. For a not-void methods returns just its return type. For a void methods,
 * reports an error.
 *
 * @author plotnikov, ptraeder
 */
public class FunctionCallVisitor implements NESTMLVisitor {

  @Override
  public void visit(final ASTExpr expr) { // visits only function calls
    checkArgument(expr.getEnclosingScope().isPresent(), "Run symboltable creator.");
    final Scope scope = expr.getEnclosingScope().get();
    checkState(expr.getFunctionCall().isPresent());
    final String functionName = expr.getFunctionCall().get().getCalleeName();

    final Optional<MethodSymbol> methodSymbol = NestmlSymbols.resolveMethod(expr.getFunctionCall().get());

    if (!methodSymbol.isPresent()) {
      final String errorMsg = AstUtils.print(expr.get_SourcePositionStart()) + " : " + "Cannot resolve the method: " + functionName;
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
            final String warnMsg = SplErrorStrings.messageImplicitConversion(
                this,
                actualTypeRep.prettyPrint(),
                expectedTypeRep.prettyPrint(),
                expr.get_SourcePositionStart());
            Log.warn(warnMsg,expr.get_SourcePositionStart());
          }
        }
      }
    }

    //set modified parameter list
    expr.getFunctionCall().get().setArgs(fullParamList);
    //convolve symbol does not have a return type set.
    //returns whatever type the second parameter is.
    if(functionName.equals("convolve")){
      //Deviations from the assumptions made here are handled in the convolveCoco
      ASTExpr bufferParameter = expr.getFunctionCall().get().getArgs().get(1);
      if(bufferParameter.getVariable().isPresent()){
        String bufferName = bufferParameter.getVariable().get().toString();
        Optional<VariableSymbol> bufferSymbolOpt = VariableSymbol.resolveIfExists(bufferName,scope);
        if(bufferSymbolOpt.isPresent()){
          expr.setType(Either.value(bufferSymbolOpt.get().getType()));
          return;
        }
      }

      //getting here means there is an error with the parameters to convolve
      final String errorMsg = NestmlErrorStrings.errorCannotCalculateConvolveResult(this);
      expr.setType(Either.error(errorMsg));
      return;
    }

    //revisit current sub-tree with substitution if a change happened
    if(needUpdate) {
      ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
      expr.accept(expressionTypeVisitor);
    }
    if (TypeChecker.isVoid(methodSymbol.get().getReturnType())) {
      final String errorMsg = NestmlErrorStrings.message(this, functionName);
      expr.setType(Either.error(errorMsg));
      return;
    }


    expr.setType(Either.value(methodSymbol.get().getReturnType()));
  }

}
