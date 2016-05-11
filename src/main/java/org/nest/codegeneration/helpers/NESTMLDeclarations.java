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
public class NESTMLDeclarations {
  private final NESTML2NESTTypeConverter nestml2NESTTypeConverter;

  private final NESTML2NESTTypeConverter typeConverter;

  public NESTMLDeclarations() {
    nestml2NESTTypeConverter = new NESTML2NESTTypeConverter();
    typeConverter = new NESTML2NESTTypeConverter();
  }

  public boolean isVectorType(final ASTAliasDecl astAliasDecl) {
    return astAliasDecl.getDeclaration().getSizeParameter().isPresent();
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
        final Optional<VariableSymbol> currVar = scope.resolve(variableName, VariableSymbol.KIND);
        checkState(currVar.isPresent(), "Cannot resolve the variable: " + variableName);
        variables.add(currVar.get());
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

  public boolean isVectorLHS(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "No scope. Run symbol table creator");
    final Scope scope = astAssignment.getEnclosingScope().get();
    final String lhsVarName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> lhsVarSymbol
        = scope.resolve(lhsVarName, VariableSymbol.KIND);

    checkState(lhsVarSymbol.isPresent(), "Cannot resolve the name: " + lhsVarName);
    return lhsVarSymbol.get().getArraySizeParameter().isPresent();
  }

  public String printSizeParameter(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(), "Run symbol table creator");
    final Scope scope = astAssignment.getEnclosingScope().get();
    // The existence of the variable is ensured by construction
    final Optional<VariableSymbol> vectorVariable = ASTNodes.getVariableSymbols(astAssignment.getExpr())
        .stream()
        .filter(VariableSymbol::isVector).findAny();
    return vectorVariable.get().getArraySizeParameter().get(); // Array parameter is ensured by the query
  }

}
