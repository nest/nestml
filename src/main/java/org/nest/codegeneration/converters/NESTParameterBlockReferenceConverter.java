/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTVariable;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;
import static org.nest.utils.AstUtils.convertSiName;

import java.util.Optional;

/**
 * Converts constants, names and functions the NEST equivalents.
 *
 * @author plotnikov
 */
public class NESTParameterBlockReferenceConverter extends NESTReferenceConverter {


  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkArgument(astVariable.getEnclosingScope().isPresent(), "Run symboltable creator");
    final String variableName = astVariable.toString();
    final Scope scope = astVariable.getEnclosingScope().get();

    Optional<String> siUnitAsLiteral = convertSiName(astVariable.toString());
    if(siUnitAsLiteral.isPresent()){
      return siUnitAsLiteral.get();
    }

    if (PredefinedVariables.E_CONSTANT.equals(variableName)) {
      return "numerics::e";
    }
    else {
      final VariableSymbol variableSymbol = resolve(variableName, scope);

      return "get_" + variableName + "()" +  (variableSymbol.isVector()?"[i]":"") ;
    }

  }

}
