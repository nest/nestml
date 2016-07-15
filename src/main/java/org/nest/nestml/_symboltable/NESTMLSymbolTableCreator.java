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
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTShape;
import org.nest.spl._ast.ASTCompound_Stmt;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTParameter;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.*;
import org.nest.symboltable.symbols.references.NeuronSymbolReference;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.trace;
import static java.util.Objects.requireNonNull;
import static java.util.Optional.empty;
import static java.util.Optional.of;
import static org.nest.symboltable.symbols.NeuronSymbol.Type.COMPONENT;
import static org.nest.symboltable.symbols.NeuronSymbol.Type.NEURON;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.LOCAL;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.STATE;
import static org.nest.utils.ASTUtils.computeTypeName;
import static org.nest.utils.ASTUtils.convertToSimpleName;

/**
 * Creates NESTML symbols.
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableCreator extends CommonSymbolTableCreator implements NESTMLVisitor {
  private String LOGGER_NAME = NESTMLSymbolTableCreator.class.getName();
  private Optional<ASTAliasDecl> astAliasDeclaration = empty();
  private Optional<ASTVar_Block> astVariableBlockType = empty();
  private Optional<NeuronSymbol> currentTypeSymbol = empty();

  public NESTMLSymbolTableCreator(
      final ResolverConfiguration resolverConfig,
      final MutableScope enclosingScope) {
    super(resolverConfig, enclosingScope);
  }

  /**
   * Creates the symbol table starting from the <code>rootNode</code> and returns the first scope
   * that was created.
   *
   * @param rootNode the root node
   * @return the first scope that was created
   */
  Scope createFromAST(final ASTNESTMLNode rootNode) {
    requireNonNull(rootNode);
    rootNode.accept(this);
    return getFirstCreatedScope();
  }


  public void visit(final ASTNESTMLCompilationUnit compilationUnitAst) {
    final List<ImportStatement> imports = computeImportStatements(compilationUnitAst);

    final MutableScope artifactScope = new ArtifactScope(
        empty(),
        compilationUnitAst.getFullName(),
        imports);
    putOnStack(artifactScope);

    final String msg = "Adds an artifact scope for the NESTML model file: " +
        compilationUnitAst.getFullName();
    trace(msg, LOGGER_NAME);
  }

  private List<ImportStatement> computeImportStatements(ASTNESTMLCompilationUnit compilationUnitAst) {
    final List<ImportStatement> imports = new ArrayList<>();

    compilationUnitAst.getImports().forEach(importStatement -> {
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
    final NeuronSymbol neuronSymbol = new NeuronSymbol(astNeuron.getName(), NEURON);

    if (astNeuron.getBase().isPresent()) {
      final NeuronSymbolReference baseSymbol = new NeuronSymbolReference(
          astNeuron.getBase().get(),
          NeuronSymbol.Type.NEURON,
          getFirstCreatedScope()
      );
      neuronSymbol.setBaseNeuron(baseSymbol);
    }
    currentTypeSymbol = Optional.of(neuronSymbol);
    addToScopeAndLinkWithNode(neuronSymbol, astNeuron);
    trace("Add symbol for the neuron:  " + astNeuron.getName(), LOGGER_NAME);
  }

  public void endVisit(final ASTNeuron astNeuron) {
    addVariablesFromODEBlock(astNeuron.getBody());
    assignOdeToVariables(astNeuron.getBody());
    removeCurrentScope();
    currentTypeSymbol = empty();
  }

  /**
   * Analyzes the ode block and add all variables, which are defined through ODEs. E.g.:
   *   state:
   *     GI nS = 0
   *   end
   *   equations:
   *      GI'' = -GI'/tau_synI
   *      GI' = GI' - GI/tau_synI
   *   end
   * Results in an additional variable for G' (first equations G''). For the sake of the simplicity
   */
  private void addVariablesFromODEBlock(final ASTBody astBody) {
    if (astBody.getODEBlock().isPresent()) {
      astBody.getODEBlock().get().getODEs()
          .stream()
          .filter(ode -> ode.getLhs().getDifferentialOrder().size() > 1)
          .forEach(this::addDerivedVariable);
    }

  }

  private void addDerivedVariable(final ASTEquation ode) {
    final String variableName = convertToSimpleName(ode.getLhs());

    final TypeSymbol type = PredefinedTypes.getType("real");
    final VariableSymbol var = new VariableSymbol(variableName);

    var.setAstNode(ode.getLhs());
    var.setType(type);
    var.setDeclaringType(currentTypeSymbol.get());
    var.setLoggable(true);
    var.setAlias(false);

    //var.setDeclaringExpression(ode.getRhs());
    var.setBlockType(VariableSymbol.BlockType.STATE);

    addToScopeAndLinkWithNode(var, ode.getLhs());

    trace("Adds new shape variable '" + var.getFullName() + "'.", LOGGER_NAME);
  }

  private void assignOdeToVariables(final ASTBody astBody) {
    if (astBody.getODEBlock().isPresent()) {
      astBody.getODEBlock().get().getODEs()
          .forEach(this::addOdeToVariable);

    }

  }

  private void addOdeToVariable(final ASTEquation ode) {
    checkState(this.currentScope().isPresent());

    final Scope scope = currentScope().get();
    final String variableName = convertToSimpleName(ode.getLhs());
    final VariableSymbol stateVariable = VariableSymbol.resolve(variableName, scope);
    stateVariable.setOdeDeclaration(ode.getRhs());

  }

  public void visit(final ASTComponent componentAst) {
    final NeuronSymbol componentSymbol = new NeuronSymbol(componentAst.getName(), COMPONENT);
    currentTypeSymbol = of(componentSymbol);

    addToScopeAndLinkWithNode(componentSymbol, componentAst);

    trace("Adds a component symbol for the component: " + componentSymbol.getFullName(), LOGGER_NAME);
  }

  public void endVisit(final ASTComponent componentAst) {
    removeCurrentScope();
    currentTypeSymbol = empty();
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

    astAliasDeclaration = Optional.of(aliasDeclAst);
    final String msg = "Sets parent alias at the position: " + aliasDeclAst.get_SourcePositionStart();
    trace(msg, LOGGER_NAME);

  }

  public void endVisit(final ASTAliasDecl aliasDeclAst) {
    astAliasDeclaration = empty();
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
      var.setVectorParameter(inputLineAst.getSizeParameter().get());
    }

    addToScopeAndLinkWithNode(var, inputLineAst);
    trace("Creates new symbol for the input buffer: " + var, LOGGER_NAME);
  }

  public void visit(final ASTFunction funcAst) {
    checkState(this.currentScope().isPresent());
    checkState(currentTypeSymbol.isPresent(), "This statement is defined in a nestml type.");

    trace(LOGGER_NAME, "Begins processing of the function: " + funcAst.getName());

    MethodSymbol methodSymbol = new MethodSymbol(funcAst.getName());

    methodSymbol.setDeclaringType(currentTypeSymbol.get());

    addToScopeAndLinkWithNode(methodSymbol, funcAst);

    // Parameters
    if (funcAst.getParameters().isPresent()) {
      for (ASTParameter p : funcAst.getParameters().get().getParameters()) {
        String typeName = computeTypeName(p.getDatatype());
        Optional<TypeSymbol> type = PredefinedTypes.getTypeIfExists(typeName);

        checkState(type.isPresent());

        methodSymbol.addParameterType(type.get());

        // add a var entry for method body
        VariableSymbol var = new VariableSymbol(p.getName());
        var.setAstNode(p);
        var.setType(type.get());

        var.setDeclaringType(null); // TOOD: make the variable optional or define a public type
        var.setBlockType(VariableSymbol.BlockType.LOCAL);
        addToScopeAndLinkWithNode(var, p);

      }

    }
    // return type
    if (funcAst.getReturnType().isPresent()) {
      final String returnTypeName = computeTypeName(funcAst.getReturnType().get());
      Optional<TypeSymbol> returnType = PredefinedTypes.getTypeIfExists(returnTypeName);

      checkState(returnType.isPresent());

      methodSymbol.setReturnType(returnType.get());

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
    astVariableBlockType = Optional.of(astVarBlock);
    trace("Handled variable_block", LOGGER_NAME);
  }



  @Override
  public void endVisit(final ASTVar_Block astVarBlock) {
    astVariableBlockType = empty();
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
    checkState(currentTypeSymbol.isPresent());
    if (this.astAliasDeclaration.isPresent()) {
      checkState(astVariableBlockType.isPresent(), "Declaration is not inside a block.");
      ASTVar_Block blockAst = astVariableBlockType.get();


      if (blockAst.isState()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol.get(),
            astAliasDeclaration.orElse(null),
            STATE);
      }
      else if (blockAst.isParameter()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol.get(),
            astAliasDeclaration.orElse(null),
            VariableSymbol.BlockType.PARAMETER);
      }
      else if (blockAst.isInternal()) {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol.get(),
            astAliasDeclaration.orElse(null),
            VariableSymbol.BlockType.INTERNAL);
      }
      else {
        addVariablesFromDeclaration(
            astDeclaration,
            currentTypeSymbol.get(),
            astAliasDeclaration.orElse(null),
            VariableSymbol.BlockType.LOCAL);
      }


    }
    else { // the declaration is defined inside a method
      addVariablesFromDeclaration(
          astDeclaration,
          currentTypeSymbol.get(),
          astAliasDeclaration.orElse(null),
          VariableSymbol.BlockType.LOCAL);

    }

  }

  /**
   * Adds variables from a declaration. Distinguishes between the place of the declaration, e.g.
   * local, state, ...
   * @param aliasDeclAst Nullable declaration which can be empty if a variable defined in a function
   *                     and not in a variable block.
   */
  private void addVariablesFromDeclaration(
      final ASTDeclaration astDeclaration,
      final NeuronSymbol currentTypeSymbol,
      final ASTAliasDecl aliasDeclAst,
      final VariableSymbol.BlockType blockType) {
    final String typeName =  computeTypeName(astDeclaration.getDatatype());
    Optional<TypeSymbol> type = PredefinedTypes.getTypeIfExists(typeName);

    for (String varName : astDeclaration.getVars()) { // multiple vars in one decl possible

      final VariableSymbol var = new VariableSymbol(varName);
      var.setAstNode(astDeclaration);
      var.setType(type.get());
      var.setDeclaringType(currentTypeSymbol);

      boolean isLoggableStateVariable = blockType == STATE && !aliasDeclAst.isSuppress();
      boolean isLoggableNonStateVariable = blockType == LOCAL || !(blockType == STATE) && aliasDeclAst.isLog();
      if (isLoggableStateVariable || isLoggableNonStateVariable) {
        // otherwise is set to false.
        var.setLoggable(true);
      }

      if (aliasDeclAst != null) {
        if (aliasDeclAst.isAlias()) {
          var.setAlias(true);
        }

        if (astDeclaration.getExpr().isPresent()) {
          var.setDeclaringExpression(astDeclaration.getExpr().get());
        }

      }

      if (astDeclaration.getSizeParameter().isPresent()) {
        var.setVectorParameter(astDeclaration.getSizeParameter().get());
      }

      var.setBlockType(blockType);
      addToScopeAndLinkWithNode(var, astDeclaration);

      trace("Adds new variable '" + var.getFullName() + "'.", LOGGER_NAME);

    }

  }

  @Override
  public void visit(final ASTShape astShape) {
    final TypeSymbol type = PredefinedTypes.getType("real");
    final VariableSymbol var = new VariableSymbol(astShape.getLhs().toString());

    var.setAstNode(astShape);
    var.setType(type);
    var.setDeclaringType(currentTypeSymbol.get());
    var.setLoggable(true);
    var.setAlias(false);
    var.setDeclaringExpression(astShape.getRhs());
    var.setBlockType(VariableSymbol.BlockType.SHAPE);

    addToScopeAndLinkWithNode(var, astShape);

    trace("Adds new shape variable '" + var.getFullName() + "'.", LOGGER_NAME);
  }

}
