/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import org.nest.codegeneration.converters.NESTML2NESTTypeConverter;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static org.nest.utils.AstUtils.computeTypeName;

/**
 * This class is used in the code generator to convert NESTML types to the NEST types
 *
 * @author plotnikov
 */
@SuppressWarnings({"unused"}) // the class is used from templates
public class ASTDeclarations {
  private final NESTML2NESTTypeConverter nestml2NESTTypeConverter;

  private final NESTML2NESTTypeConverter typeConverter;

  public ASTDeclarations() {
    nestml2NESTTypeConverter = new NESTML2NESTTypeConverter();
    typeConverter = new NESTML2NESTTypeConverter();
  }

  public boolean isVector(final ASTDeclaration astDeclaration) {
    return astDeclaration.getSizeParameter().isPresent();
  }

  public String printSizeParameter(final ASTDeclaration astDeclaration) {
    return astDeclaration.getSizeParameter().get(); // must be ensured in the calling template
  }

  public String printVariableType(final VariableSymbol variableSymbol) {

    if (variableSymbol.getVectorParameter().isPresent()) {
      return "std::vector< " + nestml2NESTTypeConverter.convert(variableSymbol.getType()) + " > ";
    }
    else {
      return nestml2NESTTypeConverter.convert(variableSymbol.getType());
    }
  }

  public String initialValue(final VariableSymbol variableSymbol) {

    if (variableSymbol.getVectorParameter().isPresent()) {
      return "std::vector< " + nestml2NESTTypeConverter.convert(variableSymbol.getType()) + " > ()";
    }
    else {
      return "0"; // TODO map it based on its type
    }
  }

  public List<VariableSymbol> getVariables(final ASTDeclaration astDeclaration) {
    checkArgument(astDeclaration.getEnclosingScope().isPresent(), "Alias has no assigned scope.");
    final List<VariableSymbol> variables = Lists.newArrayList();
    final Scope scope = astDeclaration.getEnclosingScope().get();
    final String typeName = computeTypeName(astDeclaration.getDatatype());
    final Optional<TypeSymbol> type = scope.resolve(typeName, TypeSymbol.KIND);
    if (type.isPresent()) {


      for (String variableName : astDeclaration.getVars()) {
        final VariableSymbol currVar = VariableSymbol.resolve(variableName, scope);
        variables.add(currVar);
      }

      return variables;
    }
    else {
      throw new RuntimeException("Cannot resolve the type: " + typeName);
    }
  }



  public String getDomainFromType(final TypeSymbol type) {
    checkNotNull(type);
    return typeConverter.convert(type);
  }

}
