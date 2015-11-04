/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.*;
import de.se_rwth.commons.Names;
import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.spl._ast.ASTCompound_Stmt;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.*;
import org.nest.symboltable.symbols.references.NESTMLNeuronSymbolReference;
import org.nest.symboltable.symbols.references.NESTMLTypeSymbolReference;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.info;
import static de.se_rwth.commons.logging.Log.warn;
import static java.util.Objects.requireNonNull;
import static java.util.Optional.empty;
import static org.nest.symboltable.symbols.NESTMLNeuronSymbol.Type.COMPONENT;
import static org.nest.symboltable.symbols.NESTMLNeuronSymbol.Type.NEURON;

/**
 * Visitor that creates symbols that handles nestml models..
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public interface NESTMLSymbolTableCreator extends SymbolTableCreator, NESTMLVisitor {

  String LOGGER_NAME = NESTMLSymbolTableCreator.class.getName();

  PredefinedTypesFactory getPredefinedTypesFactory();

  void setPackageName(String packageName);

  void setRoot(final ASTNESTMLCompilationUnit compilationUnitAst);

  ASTNESTMLCompilationUnit getRoot();

  String getPackageName();

  void setAliasDeclaration(final Optional<ASTAliasDecl> astAliasDeclaration);

  Optional<ASTAliasDecl> getAliasDeclaration();

  void setVariableBlockType(final Optional<ASTVar_Block> variableBlockType );

  Optional<ASTVar_Block> getVariableBlockType();

  /**
   * Creates the symbol table starting from the <code>rootNode</code> and returns the first scope
   * that was created.
   *
   * @param rootNode the root node
   * @return the first scope that was created
   */
  default Scope createFromAST(final ASTNESTMLNode rootNode) {
    requireNonNull(rootNode);
    rootNode.accept(this);
    return getFirstCreatedScope();
  }


  default void visit(final ASTNESTMLCompilationUnit compilationUnitAst) {
    final String fullName = Names.getQualifiedName(compilationUnitAst.getPackageName().getParts());
    final String packageName = Names.getQualifier(fullName);

    setRoot(compilationUnitAst);
    setPackageName(packageName);

    final List<ImportStatement> imports = computeImportStatements(compilationUnitAst);

    final MutableScope artifactScope = new ArtifactScope(empty(), fullName, imports);
    putOnStack(artifactScope);

    info("Adds an artifact scope for the NESTML model file: " + fullName, LOGGER_NAME);
  }

  default List<ImportStatement> computeImportStatements(ASTNESTMLCompilationUnit compilationUnitAst) {
    final List<ImportStatement> imports = new ArrayList<>();
    if(compilationUnitAst.getImports() != null) {

      compilationUnitAst.getImports().stream().forEach(importStatement -> {
        final String importAsString = Names.getQualifiedName(importStatement.getQualifiedName().getParts());
        imports.add(new ImportStatement(importAsString, importStatement.isStar()));
      });
    }
    return imports;
  }

  default void endVisit(final ASTNESTMLCompilationUnit compilationUnitAst) {
    final String fullName = Names.getQualifiedName(compilationUnitAst.getPackageName().getParts());

    removeCurrentScope();

    setEnclosingScopeOfNodes(compilationUnitAst);
    info("Finishes handling and sets scopes on all ASTs for the artifact: " + fullName, LOGGER_NAME);
  }

  default void visit(final ASTNeuron neuronAst) {
    info("Processes the neuron:  " + neuronAst.getName(), LOGGER_NAME);

    final NESTMLNeuronSymbol neuronSymbol = new NESTMLNeuronSymbol(neuronAst.getName(), NEURON);

    addToScopeAndLinkWithNode(neuronSymbol, neuronAst);

    info("Adds a neuron symbol: " + neuronSymbol.getFullName(), LOGGER_NAME);
  }

  default void endVisit(final ASTNeuron neuron) {
    removeCurrentScope();
    info(LOGGER_NAME, "Finishes handling of the neuron: " + neuron.getName());
  }

  default void visit(final ASTComponent componentAst) {
    info("Processes the component:  " + componentAst.getName(), LOGGER_NAME);
    final NESTMLNeuronSymbol componentSymbol = new NESTMLNeuronSymbol(componentAst.getName(), COMPONENT);

    addToScopeAndLinkWithNode(componentSymbol, componentAst);

    info("Adds a component symbol for the component: " + componentSymbol.getFullName(), LOGGER_NAME);
  }

  default void endVisit(final ASTComponent componentAst) {
    removeCurrentScope();
    info("Finishes handling of the component: " + componentAst.getName(), LOGGER_NAME);
  }

  /**
   *
   * {@code
   * Grammar
   * USE_Stmt implements BodyElement = "use" name:QualifiedName "as" alias:Name;
   *
   * Model:
   * ...
   * neuron iaf_neuron:
   *   use TestComponent as TestRef
   * ...
   * }
   *
   *
   */
  default void visit(final ASTUSE_Stmt useAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NESTMLNeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    final String referencedTypeName = Names.getQualifiedName(useAst.getName().getParts());

    final String aliasFqn = useAst.getAlias();

    // TODO it is not a reference, but a delegate
    final NESTMLNeuronSymbolReference referencedType
        = new NESTMLNeuronSymbolReference(referencedTypeName, NEURON, this.currentScope().get());
    referencedType.setAstNode(useAst);
    final NESTMLUsageSymbol usageSymbol = new NESTMLUsageSymbol(aliasFqn, referencedType);
    putInScope(usageSymbol);

    info("Handles an use statement: use " + referencedTypeName + " as " + aliasFqn, LOGGER_NAME);
  }


  // TODO: use the visitor approach
  @SuppressWarnings("unchecked") // It is OK to suppress this warning, since it is checked in the if block
  default Optional<NESTMLNeuronSymbol> computeNeuronSymbolIfExists(final Scope mutableScope) {
    if (mutableScope.getSpanningSymbol().isPresent() &&
        mutableScope.getSpanningSymbol().get() instanceof NESTMLNeuronSymbol) {

      return (Optional<NESTMLNeuronSymbol>) mutableScope.getSpanningSymbol();
    }
    else if (mutableScope.getEnclosingScope().isPresent()) {
      return computeNeuronSymbolIfExists(mutableScope.getEnclosingScope().get());
    }
    else {
      return empty();
    }

  }

  default void endVisit(final ASTUSE_Stmt useAst) {
    //removeCurrentScope();
  }

  /**
   * {@code
   * Grammar:
   * AliasDecl = ([hide:"-"])? ([alias:"alias"])? Declaration;}
   * Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expression )?;
   *
   * Model:
   */
  default void visit(final ASTAliasDecl aliasDeclAst) {
    checkState(this.currentScope().isPresent());

    final String msg = "Begins handling of an alias declaration: " + aliasDeclAst.get_SourcePositionStart();
    info(msg, LOGGER_NAME);
    setAliasDeclaration(Optional.of(aliasDeclAst));

  }

  default void endVisit(final ASTAliasDecl aliasDeclAst) {
    final String msg = "Ends handling of an alias declaration: " + aliasDeclAst.get_SourcePositionStart();
    info(msg, LOGGER_NAME);
    setAliasDeclaration(empty());
  }

  /**
   * {@code
   * Grammar:
   * InputLine =
   *   Name
   *   ("<" sizeParameter:Name ">")?
   *   "<-" InputType*
   *   (["spike"] | ["current"]);
   *
   * Model:
   * alias V_m mV[testSize] = y3 + E_L
   * }
   */
  default void visit(final ASTInputLine inputLineAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NESTMLNeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent());

    final NESTMLTypeSymbol bufferType = getPredefinedTypesFactory().getBufferType();

    final NESTMLVariableSymbol var = new NESTMLVariableSymbol(inputLineAst.getName());

    var.setType(bufferType);
    var.setDeclaringType(currentTypeSymbol.get());
    var.setAlias(false);
    var.setHidden(false);

    if (inputLineAst.isCurrent()) {
      var.setBlockType(NESTMLVariableSymbol.BlockType.INPUT_BUFFER_CURRENT);
    }
    else {
      var.setBlockType(NESTMLVariableSymbol.BlockType.INPUT_BUFFER_SPIKE);
    }

    if (inputLineAst.getSizeParameter().isPresent()) {
      var.setArraySizeParameter(inputLineAst.getSizeParameter().get());
    }

    addToScopeAndLinkWithNode(var, inputLineAst);
    info("Creates new symbol for the input buffer: " + var, LOGGER_NAME);
  }

  default void visit(final ASTFunction funcAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NESTMLNeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    info(LOGGER_NAME, "Begins processing of the function: " + funcAst.getName());

    NESTMLMethodSymbol methodSymbol = new NESTMLMethodSymbol(funcAst.getName());

    methodSymbol.setDeclaringType(currentTypeSymbol.get());
    methodSymbol.setDynamics(false);
    methodSymbol.setMinDelay(false);
    methodSymbol.setTimeStep(false);

    addToScopeAndLinkWithNode(methodSymbol, funcAst);

    // Parameters
    if (funcAst.getParameters().isPresent()) {
      for (ASTParameter p : funcAst.getParameters().get().getParameters()) {
        NESTMLTypeSymbol type = new NESTMLTypeSymbolReference(
            p.getType().toString(),
            NESTMLTypeSymbol.Type.PRIMITIVE,
            this.currentScope().get());

        methodSymbol.addParameterType(type);

        // add a var entry for method body
        NESTMLVariableSymbol var =new  NESTMLVariableSymbol(p.getName());
        var.setAstNode(p);
        var.setType(type);
        var.setAlias(false);
        var.setHidden(false);
        var.setDeclaringType(null);
        var.setBlockType(NESTMLVariableSymbol.BlockType.LOCAL);
        addToScopeAndLinkWithNode(var, p);

      }

    }
    // return type
    if (funcAst.getReturnType().isPresent()) {
      final String returnTypeName = Names.getQualifiedName(funcAst.getReturnType().get().getParts());
      NESTMLTypeSymbol returnType = new NESTMLTypeSymbolReference(
          returnTypeName,
          NESTMLTypeSymbol.Type.PRIMITIVE,
          currentScope().get());
      methodSymbol.setReturnType(returnType);
    }
    else {
      methodSymbol.setReturnType(getPredefinedTypesFactory().getVoidType());
    }

  }

  default void endVisit(final ASTFunction funcAst) {
    removeCurrentScope();
    info("Ends processing of the function: " + funcAst.getName(), LOGGER_NAME);
  }

  default void visit(final ASTDynamics dynamicsAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NESTMLNeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    final NESTMLMethodSymbol methodEntry = new NESTMLMethodSymbol("dynamics");

    methodEntry.setDeclaringType(currentTypeSymbol.get());
    methodEntry.setDynamics(true);
    methodEntry.setMinDelay(dynamicsAst.getMinDelay().isPresent());
    methodEntry.setTimeStep(dynamicsAst.getTimeStep().isPresent());

    addToScopeAndLinkWithNode(methodEntry, dynamicsAst);

    // Parameters
    if (dynamicsAst.getParameters().isPresent()) {
      for (ASTParameter p : dynamicsAst.getParameters().get().getParameters()) {
        NESTMLTypeSymbol type = new NESTMLTypeSymbolReference(
            p.getType().toString(),
            NESTMLTypeSymbol.Type.PRIMITIVE,
            currentScope().get());

        methodEntry.addParameterType(type);

        // add a var entry for method body
        NESTMLVariableSymbol var = new NESTMLVariableSymbol(p.getName());
        var.setAstNode(p);
        var.setType(type);
        var.setAlias(false);
        var.setHidden(false);
        var.setDeclaringType(null); // TODO set to optional
        var.setBlockType(NESTMLVariableSymbol.BlockType.LOCAL);
        addToScopeAndLinkWithNode(var, p);
      }

    }

    // return type
    methodEntry.setReturnType(getPredefinedTypesFactory().getVoidType());

  }


  @Override
  default void endVisit(final ASTDynamics de) {
    removeCurrentScope();
    info("Ends processing of the dynamics: ", LOGGER_NAME);
  }


  @Override
  default void visit(final ASTVar_Block astVarBlock) {
    setVariableBlockType(Optional.of(astVarBlock));
  }

  @Override
  default void endVisit(final ASTVar_Block astVarBlock) {
    setVariableBlockType(empty());
  }


  @Override
  default void visit(final ASTCompound_Stmt astCompoundStmt) {
    // TODO reuse SPLVisitor
    final CommonScope shadowingScope = new CommonScope(true);
    putOnStack(shadowingScope);
    info("Spans block scope.", LOGGER_NAME);
  }

  @Override
  default void endVisit(final ASTCompound_Stmt astCompoundStmt) {
    // TODO reuse SPLVisitor
    removeCurrentScope();
    info("Removes block scope.", LOGGER_NAME);
  }

  // TODO replication, refactor it
  @Override
  default void visit(final ASTDeclaration astDeclaration) {
    final Optional<NESTMLNeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(
        this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    final Optional<ASTAliasDecl> aliasDeclAst = getAliasDeclaration();

    if (aliasDeclAst.isPresent()) {
      Optional<ASTVar_Block> blockAst = getVariableBlockType();

      checkState(blockAst.isPresent(), "Declaration is not inside a block.");

      if (blockAst.get().isState()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            NESTMLVariableSymbol.BlockType.STATE);
      }
      else if (blockAst.get().isParameter()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            NESTMLVariableSymbol.BlockType.PARAMETER);
      }
      else if (blockAst.get().isInternal()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            NESTMLVariableSymbol.BlockType.INTERNAL);
      }
      else {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            NESTMLVariableSymbol.BlockType.LOCAL);
      }


    }
    else { // the declaration is defined inside a method
      addVariablesFromDeclaration(
          astDeclaration,
          currentTypeSymbol,
          aliasDeclAst,
          NESTMLVariableSymbol.BlockType.LOCAL);

    }

  }

  default void addVariablesFromDeclaration(
      final ASTDeclaration astDeclaration,
      final Optional<NESTMLNeuronSymbol> currentTypeSymbol,
      final Optional<ASTAliasDecl> aliasDeclAst,
      final NESTMLVariableSymbol.BlockType blockType) {
    final String typeName =  astDeclaration.getType().get().toString();

    for (String varName : astDeclaration.getVars()) { // multiple vars in one decl possible
      final Optional<NESTMLTypeSymbol> typeCandidate
          = getPredefinedTypesFactory().getPredefinedTypeIfExists(typeName);

      if (typeCandidate.isPresent()) {
        final NESTMLVariableSymbol var = new NESTMLVariableSymbol(varName);

        var.setAstNode(astDeclaration);
        var.setType(typeCandidate.get());
        var.setDeclaringType(currentTypeSymbol.get());

        if (aliasDeclAst.isPresent()) {
          var.setAlias(aliasDeclAst.get().isAlias());
          var.setHidden(aliasDeclAst.get().isHide());
        }
        else {
          var.setAlias(false);
          var.setHidden(false);
        }

        if (astDeclaration.getSizeParameter().isPresent()) {
          var.setArraySizeParameter(astDeclaration.getSizeParameter().get());
        }

        var.setBlockType(blockType);
        addToScopeAndLinkWithNode(var, astDeclaration);

        info("Adds new variable '" + var.getFullName() + "'.", LOGGER_NAME);
      }
      else {
        warn("The variable " + varName + " at " + astDeclaration.get_SourcePositionStart() +
            " is ignored. Its type is " + typeName + "it either a unit, nor a predefined.");
      }

    }

  }

}
