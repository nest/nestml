/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.*;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.spl._ast.ASTCompound_Stmt;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTParameter;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.*;
import org.nest.symboltable.symbols.references.NeuronSymbolReference;
import org.nest.symboltable.symbols.references.TypeSymbolReference;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.*;
import static java.util.Objects.requireNonNull;
import static java.util.Optional.empty;
import static org.nest.symboltable.symbols.NeuronSymbol.Type.COMPONENT;
import static org.nest.symboltable.symbols.NeuronSymbol.Type.NEURON;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.LOCAL;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.STATE;
import static org.nest.utils.ASTNodes.computeTypeName;

/**
 * Creates NESTML symbols.
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableCreator extends CommonSymbolTableCreator implements NESTMLVisitor {
  String LOGGER_NAME = NESTMLSymbolTableCreator.class.getName();
  private ASTNESTMLCompilationUnit root;
  private Optional<ASTAliasDecl> astAliasDeclaration = Optional.empty();
  private Optional<ASTVar_Block> astVariableBlockType = Optional.empty();

  public NESTMLSymbolTableCreator(
      final ResolverConfiguration resolverConfig,
      final MutableScope enclosingScope) {
    super(resolverConfig, enclosingScope);
  }

  public void setRoot(ASTNESTMLCompilationUnit root) {
    this.root = root;
  }

  public ASTNESTMLCompilationUnit getRoot() {
    return root;
  }

  public void setAliasDeclaration(final Optional<ASTAliasDecl> astAliasDeclaration) {
    this.astAliasDeclaration = astAliasDeclaration;
  }

  public Optional<ASTAliasDecl> getAliasDeclaration() {
    return astAliasDeclaration;
  }

  public void setVariableBlockType(Optional<ASTVar_Block> variableBlockType) {
    astVariableBlockType = variableBlockType;
  }

  public Optional<ASTVar_Block> getVariableBlockType() {
    return astVariableBlockType;
  }

  /**
   * Creates the symbol table starting from the <code>rootNode</code> and returns the first scope
   * that was created.
   *
   * @param rootNode the root node
   * @return the first scope that was created
   */
  public Scope createFromAST(final ASTNESTMLNode rootNode) {
    requireNonNull(rootNode);
    rootNode.accept(this);
    return getFirstCreatedScope();
  }


  public void visit(final ASTNESTMLCompilationUnit compilationUnitAst) {
    setRoot(compilationUnitAst);

    final List<ImportStatement> imports = computeImportStatements(compilationUnitAst);

    setRoot(compilationUnitAst);
    final MutableScope artifactScope = new ArtifactScope(
        empty(),
        compilationUnitAst.getFullName(),
        imports);
    putOnStack(artifactScope);

    final String msg = "Adds an artifact scope for the NESTML model file: " +
        compilationUnitAst.getFullName();
    trace(msg, LOGGER_NAME);
  }

  public List<ImportStatement> computeImportStatements(ASTNESTMLCompilationUnit compilationUnitAst) {
    final List<ImportStatement> imports = new ArrayList<>();

    compilationUnitAst.getImports().stream().forEach(importStatement -> {
      final String importAsString = Names.getQualifiedName(importStatement.getQualifiedName().getParts());
      imports.add(new ImportStatement(importAsString, importStatement.isStar()));
    });
    return imports;
  }

  public void endVisit(final ASTNESTMLCompilationUnit compilationUnitAst) {
    removeCurrentScope();
    setEnclosingScopeOfNodes(compilationUnitAst);
    final String msg = "Finishes handling and sets scopes on all ASTs for the artifact: " +
        compilationUnitAst.getFullName();
    trace(msg, LOGGER_NAME);
  }

  public void visit(final ASTNeuron astNeuron) {
    trace("Processes the neuron:  " + astNeuron.getName(), LOGGER_NAME);

    final NeuronSymbol neuronSymbol = new NeuronSymbol(astNeuron.getName(), NEURON);

    if (astNeuron.getBase().isPresent()) {
      final NeuronSymbolReference baseSymbol = new NeuronSymbolReference(
          astNeuron.getBase().get(),
          NeuronSymbol.Type.NEURON,
          getFirstCreatedScope()
      );
      neuronSymbol.setBaseNeuron(baseSymbol);
    }
    addToScopeAndLinkWithNode(neuronSymbol, astNeuron);
  }

  public void endVisit(final ASTNeuron neuron) {
    removeCurrentScope();
  }

  public void visit(final ASTComponent componentAst) {
    final NeuronSymbol componentSymbol = new NeuronSymbol(componentAst.getName(), COMPONENT);
    addToScopeAndLinkWithNode(componentSymbol, componentAst);

    trace("Adds a component symbol for the component: " + componentSymbol.getFullName(), LOGGER_NAME);
  }

  public void endVisit(final ASTComponent componentAst) {
    removeCurrentScope();
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
  public void visit(final ASTUSE_Stmt useAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    final String referencedTypeName = Names.getQualifiedName(useAst.getName().getParts());

    final String aliasFqn = useAst.getAlias();

    // TODO it is not a reference, but a delegate
    final NeuronSymbolReference referencedType
        = new NeuronSymbolReference(referencedTypeName, NEURON, this.currentScope().get());
    referencedType.setAstNode(useAst);
    final UsageSymbol usageSymbol = new UsageSymbol(aliasFqn, referencedType);
    addToScope(usageSymbol);

    trace("Handles an use statement: use " + referencedTypeName + " as " + aliasFqn, LOGGER_NAME);
  }


  // TODO: use the visitor approach
  @SuppressWarnings("unchecked") // It is OK to suppress this warning, since it is checked in the if block
  public Optional<NeuronSymbol> computeNeuronSymbolIfExists(final Scope mutableScope) {
    if (mutableScope.getSpanningSymbol().isPresent() &&
        mutableScope.getSpanningSymbol().get() instanceof NeuronSymbol) {

      return (Optional<NeuronSymbol>) mutableScope.getSpanningSymbol();
    }
    else if (mutableScope.getEnclosingScope().isPresent()) {
      return computeNeuronSymbolIfExists(mutableScope.getEnclosingScope().get());
    }
    else {
      return empty();
    }

  }
  /**
   * {@code
   * Grammar:
   * AliasDecl = ([hide:"-"])? ([alias:"alias"])? Declaration;}
   * Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expression )?;
   *
   * Model:
   */
  public void visit(final ASTAliasDecl aliasDeclAst) {
    checkState(this.currentScope().isPresent());

    setAliasDeclaration(Optional.of(aliasDeclAst));
    final String msg = "Sets parent alias at the position: " + aliasDeclAst.get_SourcePositionStart();
    trace(msg, LOGGER_NAME);

  }

  public void endVisit(final ASTAliasDecl aliasDeclAst) {
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
  public void visit(final ASTInputLine inputLineAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent());

    final TypeSymbol bufferType = PredefinedTypes.getBufferType();

    final VariableSymbol var = new VariableSymbol(inputLineAst.getName());

    var.setType(bufferType);
    var.setDeclaringType(currentTypeSymbol.get());


    if (inputLineAst.isCurrent()) {
      var.setBlockType(VariableSymbol.BlockType.INPUT_BUFFER_CURRENT);
    }
    else {
      var.setBlockType(VariableSymbol.BlockType.INPUT_BUFFER_SPIKE);
    }

    if (inputLineAst.getSizeParameter().isPresent()) {
      var.setArraySizeParameter(inputLineAst.getSizeParameter().get());
    }

    addToScopeAndLinkWithNode(var, inputLineAst);
    trace("Creates new symbol for the input buffer: " + var, LOGGER_NAME);
  }

  public void visit(final ASTFunction funcAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    trace(LOGGER_NAME, "Begins processing of the function: " + funcAst.getName());

    MethodSymbol methodSymbol = new MethodSymbol(funcAst.getName());

    methodSymbol.setDeclaringType(currentTypeSymbol.get());

    addToScopeAndLinkWithNode(methodSymbol, funcAst);

    // Parameters
    if (funcAst.getParameters().isPresent()) {
      for (ASTParameter p : funcAst.getParameters().get().getParameters()) {
        TypeSymbol type = new TypeSymbolReference(
            computeTypeName(p.getDatatype()),
            TypeSymbol.Type.PRIMITIVE,
            this.currentScope().get());

        methodSymbol.addParameterType(type);

        // add a var entry for method body
        VariableSymbol var = new VariableSymbol(p.getName());
        var.setAstNode(p);
        var.setType(type);
        var.setDeclaringType(null); // TOOD: make the variable optional or define a public type
        var.setBlockType(VariableSymbol.BlockType.LOCAL);
        addToScopeAndLinkWithNode(var, p);

      }

    }
    // return type
    if (funcAst.getReturnType().isPresent()) {
      final String returnTypeName = computeTypeName(funcAst.getReturnType().get());
      TypeSymbol returnType = new TypeSymbolReference(
          returnTypeName,
          TypeSymbol.Type.PRIMITIVE,
          currentScope().get());
      methodSymbol.setReturnType(returnType);
    }
    else {
      methodSymbol.setReturnType(PredefinedTypes.getVoidType());
    }

  }

  public void endVisit(final ASTFunction funcAst) {
    removeCurrentScope();
  }

  public void visit(final ASTDynamics dynamicsAst) {
    checkState(this.currentScope().isPresent());
    final Optional<NeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(this.currentScope().get());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    final MethodSymbol methodEntry = new MethodSymbol("dynamics");

    methodEntry.setDeclaringType(currentTypeSymbol.get());
    methodEntry.setDynamics(true);
    methodEntry.setReturnType(PredefinedTypes.getVoidType());
    addToScopeAndLinkWithNode(methodEntry, dynamicsAst);
    trace("Adds symbol for the dynamics", LOGGER_NAME);
  }


  @Override
  public void endVisit(final ASTDynamics de) {
    removeCurrentScope();
  }


  @Override
  public void visit(final ASTVar_Block astVarBlock) {
    setVariableBlockType(Optional.of(astVarBlock));
    trace("Handled variable_block", LOGGER_NAME);
  }



  @Override
  public void endVisit(final ASTVar_Block astVarBlock) {
    setVariableBlockType(empty());
  }



  @Override
  public void visit(final ASTCompound_Stmt astCompoundStmt) {
    // TODO reuse SPLVisitor
    final CommonScope shadowingScope = new CommonScope(true);
    putOnStack(shadowingScope);
    astCompoundStmt.setEnclosingScope(shadowingScope);
    trace("Spans block scope.", LOGGER_NAME);
  }

  @Override
  public void endVisit(final ASTCompound_Stmt astCompoundStmt) {
    // TODO reuse SPLVisitor
    removeCurrentScope();
    trace("Removes block scope.", LOGGER_NAME);
  }

  // TODO replication, refactor it
  @Override
  public void visit(final ASTDeclaration astDeclaration) {
    final Optional<NeuronSymbol> currentTypeSymbol = computeNeuronSymbolIfExists(
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
            STATE);
      }
      else if (blockAst.get().isParameter()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            VariableSymbol.BlockType.PARAMETER);
      }
      else if (blockAst.get().isInternal()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            VariableSymbol.BlockType.INTERNAL);
      }
      else {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol,
            aliasDeclAst,
            VariableSymbol.BlockType.LOCAL);
      }


    }
    else { // the declaration is defined inside a method
      addVariablesFromDeclaration(
          astDeclaration,
          currentTypeSymbol,
          aliasDeclAst,
          VariableSymbol.BlockType.LOCAL);

    }

  }

  /**
   * Adds variables from a declaration. Distinguishes between the place of the declaration, e.g.
   * local, state, ...
   * @param aliasDeclAst optional declaration which can be empty if a variable defined in a function
   *                     and not in a variable block.
   */
  public void addVariablesFromDeclaration(
      final ASTDeclaration astDeclaration,
      final Optional<NeuronSymbol> currentTypeSymbol,
      final Optional<ASTAliasDecl> aliasDeclAst,
      final VariableSymbol.BlockType blockType) {
    final String typeName =  computeTypeName(astDeclaration.getDatatype());

    for (String varName : astDeclaration.getVars()) { // multiple vars in one decl possible
      final Optional<TypeSymbol> typeCandidate
          = PredefinedTypes.getPredefinedTypeIfExists(typeName);

      if (typeCandidate.isPresent()) {
        final VariableSymbol var = new VariableSymbol(varName);

        var.setAstNode(astDeclaration);
        var.setType(typeCandidate.get());
        var.setDeclaringType(currentTypeSymbol.get());

        boolean isLoggableStateVariable = blockType == STATE && !aliasDeclAst.get().isSuppress();
        boolean isLoggableNonStateVariable
            = blockType == LOCAL || !(blockType == STATE) && aliasDeclAst.get().isLog();
        if (isLoggableStateVariable || isLoggableNonStateVariable) {
          // otherwise is set to false.
          var.setLoggable(true);
        }

        if (aliasDeclAst.isPresent()) {
          if (aliasDeclAst.get().isAlias()) {
            var.setAlias(true);

            if (astDeclaration.getExpr().isPresent()) {
              var.setDeclaringExpression(astDeclaration.getExpr().get());
            }

          }

        }

        if (astDeclaration.getSizeParameter().isPresent()) {
          var.setArraySizeParameter(astDeclaration.getSizeParameter().get());
        }

        var.setBlockType(blockType);
        addToScopeAndLinkWithNode(var, astDeclaration);

        trace("Adds new variable '" + var.getFullName() + "'.", LOGGER_NAME);
      }
      else {
        warn("The variable " + varName + " at " + astDeclaration.get_SourcePositionStart() +
            " is ignored. Its type is " + typeName + "it either a unit, nor a predefined.");
      }

    }

  }

}
