/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._visitor;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.nestml._symboltable.NESTMLSymbolTableCreator;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.typechecking.TypeChecker;
import org.nest.nestml._symboltable.NestmlSymbols;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

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


      /*
      ASTExpr bufferParameter = expr.getFunctionCall().get().getArgs().get(1);
      //reject any bufferParameter that is not simply a variable
      if(!bufferParameter.variableIsPresent()){
        final String errorMsg = NestmlErrorStrings.errorConvolveParameterNotAVariable(this);
        expr.setType(Either.error(errorMsg));
        return;
      }
      //determine type of bufferParameter
      final String bufferName = bufferParameter.getVariable().get().toString();
      Optional<VariableSymbol> bufferSymbolOpt = VariableSymbol.resolveIfExists(bufferName,scope);
      //try resolving bufferParameter: error on fail.
      if(!bufferSymbolOpt.isPresent()){
        final String errorMsg = NestmlErrorStrings.errorConvolveParameterNotResolvable(this,bufferName);
        expr.setType(Either.error(errorMsg));
        return;
      }
      //check that bufferParameter is a buffer
      final VariableSymbol bufferSymbol = bufferSymbolOpt.get();
      if(!bufferSymbol.getType().getType().equals(TypeSymbol.Type.BUFFER)){
        final String errorMsg = NestmlErrorStrings.errorConvolveParameterMustBeBuffer(this);
        expr.setType(Either.error(errorMsg));
        return;
      }

      expr.setType(Either.value(bufferSymbol.getType()));
      return;*/
    }

    if (TypeChecker.isVoid(methodSymbol.get().getReturnType())) {
      final String errorMsg = NestmlErrorStrings.message(this, functionName);
      expr.setType(Either.error(errorMsg));
      return;
    }


    expr.setType(Either.value(methodSymbol.get().getReturnType()));
  }

}
