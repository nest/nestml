/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import org.nest.codegeneration.helpers.Names;
import org.nest.nestml._ast.ASTVariable;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.nestml._symboltable.symbols.VariableSymbol.resolve;
import static org.nest.utils.AstUtils.convertSiName;

import java.util.Optional;

/**
 * Converts constants, names and functions the NEST equivalents.
 *
 * @author plotnikov
 */
public class NESTStateBlockReferenceConverter extends NESTReferenceConverter {

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkArgument(astVariable.getEnclosingScope().isPresent(), "Run symboltable creator");
    final String variableName = astVariable.toString();
    final Scope scope = astVariable.getEnclosingScope().get();
    final VariableSymbol variableSymbol = resolve(variableName, scope);

    Optional<String> siUnitAsLiteral = convertSiName(astVariable.toString());
    if(siUnitAsLiteral.isPresent()){
      return siUnitAsLiteral.get();
    }

    return (variableSymbol.isParameter()?"__p.":"") + Names.getter(variableSymbol) + "()";
  }

}
