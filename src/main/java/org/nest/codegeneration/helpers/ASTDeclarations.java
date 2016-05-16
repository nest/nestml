/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.codegeneration.converters.NESTML2NESTTypeConverter;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.*;
import static org.nest.utils.ASTNodes.computeTypeName;

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

  // TODO where is this used?
  public boolean isVectorType(final ASTAliasDecl astAliasDecl) {
    return astAliasDecl.getDeclaration().getSizeParameter().isPresent();
  }

  public boolean isVector(final ASTDeclaration astDeclaration) {
    return astDeclaration.getSizeParameter().isPresent();
  }

  public String printSizeParameter(final ASTDeclaration astDeclaration) {
    return astDeclaration.getSizeParameter().get(); // must be ensured in the calling template
  }

  public String printVariableType(final VariableSymbol variableSymbol) {

    if (variableSymbol.getArraySizeParameter().isPresent()) {
      return "std::vector< " + nestml2NESTTypeConverter.convert(variableSymbol.getType()) + " > ";
    }
    else {
      return nestml2NESTTypeConverter.convert(variableSymbol.getType());
    }
  }


  public List<VariableSymbol> getVariables(final ASTAliasDecl astAliasDecl) {
    return getVariables(astAliasDecl.getDeclaration());
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

  public String getAliasOrigin(final VariableSymbol variableSymbol) {
    switch (variableSymbol.getBlockType()) {
      case STATE:
        return  "S_";
      case PARAMETER:
        return  "P_";
      case INTERNAL:
        return  "V_";
      default:
        return "";
    }

  }

  public String getDomainFromType(final TypeSymbol type) {
    checkNotNull(type);

    if (type.getType().equals(TypeSymbol.Type.UNIT)) {
      return  "nest::double_t";
    }
    else {
      return typeConverter.convert(type);
    }

  }

}
