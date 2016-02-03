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

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static org.nest.utils.ASTNodes.computeTypeName;

/**
 * TODO
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

  public String getType(final ASTDeclaration astDeclaration) {
    checkArgument(astDeclaration.getEnclosingScope().isPresent());

    final Scope scope = astDeclaration.getEnclosingScope().get();
    final String declarationTypeName = computeTypeName(astDeclaration.getDatatype());

    Optional<TypeSymbol> declarationTypeSymbol = scope.resolve(declarationTypeName, TypeSymbol.KIND);
    checkState(declarationTypeSymbol.isPresent(), "Cannot resolve the NESTML type: " + declarationTypeName);

    return new NESTML2NESTTypeConverter().convert(declarationTypeSymbol.get());
  }


  public List<String> getVariables(final ASTDeclaration astDeclaration) {
    return astDeclaration.getVars();
  }

  public boolean isVectorType(final ASTAliasDecl astAliasDecl) {
    return astAliasDecl.getDeclaration().getSizeParameter().isPresent();
  }

  public String getDeclarationType(final ASTDeclaration astDeclaration) {
    checkArgument(astDeclaration.getEnclosingScope().isPresent());

    final Scope scope = astDeclaration.getEnclosingScope().get();
    final String typeName = computeTypeName(astDeclaration.getDatatype());

    Optional<TypeSymbol> typeSymbol = scope.resolve(typeName, TypeSymbol.KIND);
    checkState(typeSymbol.isPresent(), "Cannot resolve the type: " + typeName);


    if (astDeclaration.getSizeParameter().isPresent()) {
      return "std::vector< " + nestml2NESTTypeConverter.convert(typeSymbol.get()) + " > ";
    }
    else {
      return nestml2NESTTypeConverter.convert(typeSymbol.get());
    }
  }

  public String getType(final ASTAliasDecl astAliasDecl) {
    return getDeclarationType(astAliasDecl.getDeclaration());
  }

  public List<VariableSymbol> getVariables(final ASTAliasDecl astAliasDecl) {
    checkArgument(astAliasDecl.getEnclosingScope().isPresent(), "Alias has no assigned scope.");
    final Scope scope = astAliasDecl.getEnclosingScope().get();
    final ASTDeclaration decl = astAliasDecl.getDeclaration();

    final String typeName = computeTypeName(decl.getDatatype());
    final Optional<TypeSymbol> type = scope.resolve(typeName, TypeSymbol.KIND);
    if (type.isPresent()) {
      final List<VariableSymbol> variables = Lists.newArrayList();

      for (String variableName : decl.getVars()) {
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

  public String getAliasOrigin(final ASTAliasDecl astAliasDecl) {
    checkArgument(astAliasDecl.getEnclosingScope().isPresent(), "No scope. Run symbol table creator");
    final Scope scope = astAliasDecl.getEnclosingScope().get();
    final ASTDeclaration decl = astAliasDecl.getDeclaration();
    final String typeName = computeTypeName(decl.getDatatype());
    final Optional<TypeSymbol> type = scope.resolve(typeName, TypeSymbol.KIND);
    if (type.isPresent()) {
      final List<VariableSymbol> variables = Lists.newArrayList();

      for (String var : decl.getVars()) {
        final Optional<VariableSymbol> currVar = scope.resolve(var, VariableSymbol.KIND);
        variables.add(currVar.get());
      }

      if (!variables.isEmpty()) {
        final VariableSymbol first = variables.get(0);
        switch (first.getBlockType()) {
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

    }
    else {
      throw new RuntimeException("Cannot resolve the type: " + typeName);
    }
    return "";
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
    checkArgument(astAssignment.getEnclosingScope().isPresent(),
        "No scope. Run symbol table creator");
    final Scope scope = astAssignment.getEnclosingScope().get();
    final String lhsVarName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> lhsVarSymbol
        = scope.resolve(lhsVarName, VariableSymbol.KIND);

    checkState(lhsVarSymbol.isPresent(), "Cannot resolve the name: " + lhsVarName);
    return lhsVarSymbol.get().getArraySizeParameter().isPresent();
  }

  public String printSizeParameter(final ASTAssignment astAssignment) {
    checkArgument(astAssignment.getEnclosingScope().isPresent(),
        "No scope. Run symbol table creator");
    final Scope scope = astAssignment.getEnclosingScope().get();
    final String lhsVarName = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    final Optional<VariableSymbol> lhsVarSymbol
        = scope.resolve(lhsVarName, VariableSymbol.KIND);

    checkState(lhsVarSymbol.isPresent(), "Cannot resolve the name: " + lhsVarName);
    checkState(lhsVarSymbol.get().getArraySizeParameter().isPresent());
    return lhsVarSymbol.get().getArraySizeParameter().get();
  }

}
