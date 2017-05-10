/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import org.nest.codegeneration.helpers.GslNames;
import org.nest.commons._ast.ASTVariable;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.codegeneration.helpers.VariableHelper.printOrigin;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;

/**
 * Converts constants, names and functions the NEST equivalents.
 *
 * @author plotnikov
 */
public class NESTArrayStateReferenceConverter extends NESTReferenceConverter {

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkArgument(astVariable.getEnclosingScope().isPresent(), "Run symboltable creator");
    final String variableName = AstUtils.convertDevrivativeNameToSimpleName(astVariable);
    final Scope scope = astVariable.getEnclosingScope().get();

    if (PredefinedVariables.E_CONSTANT.equals(variableName)) {
      return "numerics::e";
    }
    else {
      final VariableSymbol variableSymbol = resolve(variableName, scope);
      if (variableSymbol.isState()) {
        return "S_." + GslNames.name(variableSymbol); // TODO refactor me
      }
      else if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
        return variableName + (variableSymbol.isVector()?"[i]":"");
      }
      else if(variableSymbol.isBuffer()) {
        return printOrigin(variableSymbol) + org.nest.codegeneration.helpers.Names.bufferValue(variableSymbol) ;
      }
      else {
        if (variableSymbol.isFunction()) {
          return "get_" + variableName + "()" +  (variableSymbol.isVector()?"[i]":"") ;
        }
        else {

          return printOrigin(variableSymbol) + variableName +  (variableSymbol.isVector()?"[i]":"");
        }

      }

    }

  }

}
