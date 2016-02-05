/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

import com.google.common.collect.ImmutableList;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import org.nest.commons.commons._ast.ASTBLOCK_CLOSE;
import org.nest.commons.commons._ast.ASTBLOCK_OPEN;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;

/**
 * Provides convenient  functions to statically type interfaces astnodes resulting from the Body-grammar
 * production.
 *
 * @author plotnikov
 */
public class ASTBody extends ASTBodyTOP {

  public ASTBody() {
    // this constructor is used in the generated code.
  }

  public ASTBody(
      final ASTBLOCK_OPEN bLOCK_open,
      final List<String> nEWLINEs,
      final List<ASTBodyElement> bodyElements,
      final ASTBLOCK_CLOSE bLOCK_close) {
    super(bLOCK_open, nEWLINEs, bodyElements, bLOCK_close);
  }

  public List<ASTFunction> getFunctions() {
    List<ASTFunction> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTFunction)
        .map(be -> (ASTFunction) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTDynamics> getDynamics() {
    List<ASTDynamics> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTDynamics)
        .map(be -> (ASTDynamics) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public Optional<ASTBodyElement> getStateBlock() {
    return this.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isState())
        .findFirst();
  }

  public Optional<ASTBodyElement> getParameterBlock() {
    return this.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isParameter())
        .findFirst();
  }

  public List<ASTAliasDecl> getStates() {
    List<ASTAliasDecl> result = new ArrayList<ASTAliasDecl>();

    this.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;
      if (block.isState()) {
        for (ASTAliasDecl ad : block.getAliasDecls()) {
          result.add(ad);
        }
      }
    });

    return ImmutableList.copyOf(result);
  }

  @SuppressWarnings("unused") // used in templates
  public List<ASTAliasDecl> getAliasStates() {
    return getStates().stream().filter(decl->decl.isAlias()).collect(toList());
  }

  @SuppressWarnings("unused") // used in templates
  public List<VariableSymbol> getStateAliasSymbols() {
    checkState(this.getEnclosingScope().isPresent());
    final Scope scope = this.getEnclosingScope().get();
    final List<ASTAliasDecl> aliasDeclarations = getStates().stream()
        .filter(decl -> decl.isAlias())
        .collect(toList());

    List<VariableSymbol> aliasSymbols = aliasDeclarations.stream()
        .map(alias -> {
          Optional<VariableSymbol> varSymbol = scope
              .resolve(alias.getDeclaration().getVars().get(0), VariableSymbol.KIND);
          return varSymbol.get();
        })
        .collect(toList());
    return aliasSymbols;
  }

  @SuppressWarnings("unused") // used in templates
  public List<VariableSymbol> getStateNonAliasSymbols() {
    checkState(this.getEnclosingScope().isPresent());
    final Scope scope = this.getEnclosingScope().get();
    final List<ASTAliasDecl> aliasDeclarations = getStates().stream()
        .filter(decl -> !decl.isAlias())
        .collect(toList());

    List<VariableSymbol> aliasSymbols = aliasDeclarations.stream()
        .flatMap(alias -> alias.getDeclaration().getVars().stream())
        .map(variableName ->
        { Optional<VariableSymbol> varSymbol = scope.resolve(variableName, VariableSymbol.KIND);
          return varSymbol.get();})
        .collect(toList());
    return aliasSymbols;
  }

  @SuppressWarnings("unused") // used in templates
  public List<ASTAliasDecl> getNonAliasStates() {
    return getStates().stream().filter(v->!v.isAlias()).collect(toList());
  }

  public List<ASTAliasDecl> getParameters() {
    List<ASTAliasDecl> result = new ArrayList<ASTAliasDecl>();

    this.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;
      if (block.isParameter()) {
        result.addAll(block.getAliasDecls().stream().collect(Collectors.toList()));
      }
    });

    return ImmutableList.copyOf(result);
  }

  public List<ASTAliasDecl> getAliasParameters() {

    return getParameters().stream().filter(decl -> decl.isAlias()).collect(toList());
  }

  @SuppressWarnings("unused") // used in templates
  public List<ASTAliasDecl> getNonAliasParameters() {

    return getParameters().stream().filter(decl -> !decl.isAlias()).collect(toList());
  }

  public List<ASTAliasDecl> getInternals() {
    List<ASTAliasDecl> result = new ArrayList<ASTAliasDecl>();

    this.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isInternal()) {
        for (ASTAliasDecl ad : block.getAliasDecls()) {
          result.add(ad);
        }
      }
    });

    return ImmutableList.copyOf(result);
  }

  public Optional<ASTOdeDeclaration> getEquations() {
    final Optional<ASTEquations> equations = findEquationsBlock();
    if (equations.isPresent()) {
      return Optional.of(equations.get().getOdeDeclaration());
    }
    else {
      return Optional.empty();
    }
  }

  private Optional<ASTEquations> findEquationsBlock() {
    final Optional<ASTBodyElement> equations = this.getBodyElements()
        .stream()
        .filter(be -> be instanceof ASTEquations)
        .findFirst();
    if (equations.isPresent()) {
      // only ASTEquations are filtered
      return Optional.of((ASTEquations) equations.get());
    }
    else {
      return Optional.empty();
    }
  }



  public void addToInternalBlock(final ASTAliasDecl astAliasDecl) {
    this.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isInternal()) {
        block.getAliasDecls().add(astAliasDecl);
      }

    });

  }

  public void addToStateBlock(final ASTAliasDecl astAliasDecl) {
    this.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isState()) {
        block.getAliasDecls().add(astAliasDecl);
      }

    });

  }

  private Optional<ASTBodyElement> findDynamics() {
    return this.getBodyElements().stream()
          .filter(be -> be instanceof ASTDynamics)
          .findFirst();
  }

  @SuppressWarnings("unchecked")
  public List<ASTAliasDecl> getAliasInternals() {
    return getInternals().stream().filter(decl -> decl.isAlias()).collect(toList());
  }

  @SuppressWarnings("unchecked")
  public List<ASTAliasDecl> getNonAliasInternals() {

    return getInternals().stream().filter(decl -> !decl.isAlias()).collect(toList());
  }

  public List<ASTUSE_Stmt> getUses() {
    List<ASTUSE_Stmt> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTUSE_Stmt)
        .map(be -> (ASTUSE_Stmt) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTInputLine> getInputLines() {
    List<ASTInputLine> result = new ArrayList<ASTInputLine>();

    for (ASTBodyElement be : this.getBodyElements()) {
      if (be instanceof ASTInput) {
        ASTInput in = (ASTInput) be;
        for (ASTInputLine inline : in.getInputLines()) {
          result.add(inline);
        }
      }
    }

    return ImmutableList.copyOf(result);
  }

  public List<ASTOutput> getOutputs() {
    List<ASTOutput> result = this.getBodyElements().stream()
        .filter(be -> be instanceof ASTOutput)
        .map(be -> (ASTOutput) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTStructureLine> getStructure() {
    List<ASTStructureLine> result = new ArrayList<ASTStructureLine>();

    for (ASTBodyElement be : this.getBodyElements()) {
      if (be instanceof ASTStructure) {
        ASTStructure st = (ASTStructure) be;
        for (ASTStructureLine stline : st.getStructureLines()) {
          result.add(stline);
        }
      }
    }

    return ImmutableList.copyOf(result);
  }
}
