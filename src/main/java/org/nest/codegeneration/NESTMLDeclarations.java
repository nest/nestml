/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;
import org.nest.utils.CachedResolver;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;

/**
 * TODO
 *
 * @author plotnikov
 * @since 0.0.1
 */
@SuppressWarnings({"unused"}) // the class is used from templates
public class NESTMLDeclarations {
  private final PredefinedTypesFactory typesFactory;

  final private CachedResolver cachedResolver = new CachedResolver();

  private final NESTML2NESTTypeConverter nestml2NESTTypeConverter;

  private final NESTML2NESTTypeConverter typeConverter;

  public NESTMLDeclarations(PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
    nestml2NESTTypeConverter = new NESTML2NESTTypeConverter(typesFactory);
    typeConverter = new NESTML2NESTTypeConverter(typesFactory);
  }

  public String getType(final ASTDeclaration astDeclaration) {
    checkArgument(astDeclaration.getEnclosingScope().isPresent());

    final Scope scope = astDeclaration.getEnclosingScope().get();
    final String declarationTypeName = printDeclarationTypeName(astDeclaration);

    Optional<NESTMLTypeSymbol> declarationTypeSymbol = cachedResolver.resolveAndCache(scope, declarationTypeName);
    checkState(declarationTypeSymbol.isPresent(), "Cannot resolve the NESTML type: " + declarationTypeName);

    return new NESTML2NESTTypeConverter(typesFactory).convert(declarationTypeSymbol.get());
  }

  private String printDeclarationTypeName(ASTDeclaration astDeclaration) {
    if (astDeclaration.getPrimitiveType().isPresent()) {
      return astDeclaration.getPrimitiveType().get().toString();
    }
    else if (astDeclaration.getType().isPresent()) {
      final String typeName = Names.getQualifiedName(astDeclaration.getType().get().getParts());
      return typeName;
    }
    throw new RuntimeException("Impossible by the grammar definition. One of alternatives must be used;");
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
    final String typeName = computeDeclarationTypeName(astDeclaration);

    Optional<NESTMLTypeSymbol> typeSymbol = scope.resolve(typeName, NESTMLTypeSymbol.KIND);
    checkState(typeSymbol.isPresent(), "Cannot resolve the type: " + typeName);


    if (astDeclaration.getSizeParameter().isPresent()) {
      return "std::vector< " + nestml2NESTTypeConverter.convert(typeSymbol.get()) + " > ";
    }
    else {
      return nestml2NESTTypeConverter.convert(typeSymbol.get());
    }
  }

  private String computeDeclarationTypeName(ASTDeclaration astDeclaration) {
    if (astDeclaration.getPrimitiveType().isPresent()) {
      return astDeclaration.getPrimitiveType().get().toString(); // TODO it is not really portable
    }
    else if (astDeclaration.getType().isPresent()) {
      final String typeName = Names.getQualifiedName(astDeclaration.getType().get().getParts());
      return typeName;
    }
    throw new RuntimeException("Impossible by the grammar definition. One of alternatives muste be used;");
  }

  public String getType(final ASTAliasDecl astAliasDecl) {
    return getDeclarationType(astAliasDecl.getDeclaration());
  }

  public List<NESTMLVariableSymbol> getVariables(final ASTAliasDecl astAliasDecl) {
    checkArgument(astAliasDecl.getEnclosingScope().isPresent(), "Alias has no assigned scope.");
    final Scope scope = astAliasDecl.getEnclosingScope().get();
    final ASTDeclaration decl = astAliasDecl.getDeclaration();

    final String typeName = Names.getQualifiedName(decl.getType().get().getParts());
    final Optional<NESTMLTypeSymbol> type = cachedResolver.resolveAndCache(scope, typeName);
    if (type.isPresent()) {
      final List<NESTMLVariableSymbol> variables = Lists.newArrayList();

      for (String variableName : decl.getVars()) {
        final Optional<NESTMLVariableSymbol> currVar = scope.resolve(variableName, NESTMLVariableSymbol.KIND);
        checkState(currVar.isPresent(), "Cannot resolve the variable: " + variableName);
        variables.add(currVar.get());
      }

      return variables;
    }
    else {
      throw new RuntimeException("Cannot resolve the type: " + decl.getType().get());
    }

  }

  public String getAliasOrigin(final ASTAliasDecl astAliasDecl) {
    checkArgument(astAliasDecl.getEnclosingScope().isPresent(), "No scope. Run symbol table creator");
    final Scope scope = astAliasDecl.getEnclosingScope().get();
    final ASTDeclaration decl = astAliasDecl.getDeclaration();
    final String typeName = Names.getQualifiedName(decl.getType().get().getParts());
    final Optional<NESTMLTypeSymbol> type = cachedResolver.resolveAndCache(scope, typeName);
    if (type.isPresent()) {
      final List<NESTMLVariableSymbol> variables = Lists.newArrayList();

      for (String var : decl.getVars()) {
        final Optional<NESTMLVariableSymbol> currVar = scope.resolve(var, NESTMLVariableSymbol.KIND);
        variables.add(currVar.get());
      }

      if (!variables.isEmpty()) {
        final NESTMLVariableSymbol first = variables.get(0);
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

  public String getDomainFromType(final NESTMLTypeSymbol type) {
    checkNotNull(type);

    if (type.getType().equals(NESTMLTypeSymbol.Type.UNIT)) {
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
    final Optional<NESTMLVariableSymbol> lhsVarSymbol
        = scope.resolve(lhsVarName, NESTMLVariableSymbol.KIND);

    checkState(lhsVarSymbol.isPresent(), "Cannot resolve the name: " + lhsVarName);
    return lhsVarSymbol.get().getArraySizeParameter().isPresent();
  }


}
