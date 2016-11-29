/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import org.nest.codegeneration.helpers.Names;
import org.nest.commons._ast.ASTVariable;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;

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

    return (variableSymbol.isParameters ()?"__p.":"") + Names.getter(variableSymbol) + "()";
  }

}
