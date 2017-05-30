/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.*;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.*;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units._visitor.UnitsSIVisitor;
import org.nest.units.unitrepresentation.UnitRepresentation;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.trace;
import static java.util.Objects.requireNonNull;
import static java.util.Optional.empty;
import static java.util.Optional.of;
import static org.nest.codegeneration.sympy.OdeTransformer.getCondSumFunctionCall;
import static org.nest.symboltable.symbols.NeuronSymbol.Type.NEURON;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.STATE;
import static org.nest.utils.AstUtils.computeTypeName;
import static org.nest.utils.AstUtils.getNameOfLHS;

/**
 * Creates NESTML symbols.
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableCreator extends CommonSymbolTableCreator implements NESTMLVisitor {
  private static String LOGGER_NAME = "NESTML_SymbolTableCreator";
  private Optional<NeuronSymbol> currentTypeSymbol = empty();
  private Optional<ASTVar_Block> varBlock = empty();

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
    //TODO Maybe find a better place for this
    UnitsSIVisitor.convertSiUnitsToSignature(rootNode);
    rootNode.accept(this);
    return getFirstCreatedScope();
  }


  public void visit(final ASTNESTMLCompilationUnit compilationUnitAst) {

    final MutableScope artifactScope = new ArtifactScope(
        empty(),
        compilationUnitAst.getFullName(),
        Lists.newArrayList());
    putOnStack(artifactScope);

    final String msg = "Adds an artifact scope for the NESTML model file: " + compilationUnitAst.getFullName();
    trace(msg, LOGGER_NAME);
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
    currentTypeSymbol = Optional.of(neuronSymbol);
    addToScopeAndLinkWithNode(neuronSymbol, astNeuron);
    trace("Add symbol for the neuron:  " + astNeuron.getName(), LOGGER_NAME);
  }

  public void endVisit(final ASTNeuron astNeuron) {
    setEnclosingScopeOfNodes(astNeuron);

    if (astNeuron.getBody().getODEBlock().isPresent()) {
      addFunctionVariables(astNeuron.getBody().getODEBlock().get());
    }

    // new variable from the ODE block could be added. Check, whether they don't clutter with existing one
    final NestmlCoCosManager nestmlCoCosManager = new NestmlCoCosManager();

    if (astNeuron.getBody().getODEBlock().isPresent()) {
      addVariablesFromODEBlock(astNeuron.getBody().getODEBlock().get());
    }

    final List<Finding> findings = nestmlCoCosManager.checkThatVariablesDefinedOnce(astNeuron);
    if (findings.isEmpty()) {
      if (astNeuron.getBody().getODEBlock().isPresent()) {

        final List<Finding> afterAddingDerivedVariables = nestmlCoCosManager.checkThatVariablesDefinedOnce(astNeuron);

        if (afterAddingDerivedVariables.isEmpty()) {
          assignOdeToVariables(astNeuron.getBody().getODEBlock().get());
          markConductanceBasedBuffers(astNeuron.getBody().getODEBlock().get(), astNeuron.getBody().getInputLines());
        }
        else {
          final String msg = LOGGER_NAME + ": Cannot correctly build the symboltable, at least one variable is " +
                             "defined multiple times";
          Log.error(msg);
        }

      }

    }
    else {
      final String msg = LOGGER_NAME + ": Cannot correctly build the symboltable, at least one variable is " +
                         "defined multiple times";
      Log.error(msg);
    }

    removeCurrentScope();
    currentTypeSymbol = empty();
  }

  /**
   * Analyzes the ode block and adds all variables, which are defined through ODEs. E.g.:
   *   state:
   *     GI nS = 0
   *   end
   *   equations:
   *      GI'' = -GI'/tau_synI
   *      GI' = GI' - GI/tau_synI
   *   end
   * Results in an additional variable for G' (first equations G''). For the sake of the simplicity
   */
  private void addVariablesFromODEBlock(final ASTOdeDeclaration astOdeDeclaration) {
    astOdeDeclaration.getODEs()
          .stream()
          .filter(ode -> ode.getLhs().getDifferentialOrder().size() > 1)
          .forEach(this::addDerivedVariable);

  }

  /**
   * Analyzes the ode block and add all aliases. E.g.:
   *   equations:
   *      I_syn pA = I_exc - I_inh # <- inplace function
   *      V_m mV = I_syn / 1 ms
   *   end
   * Results in an additional variable for G' (first equations G''). For the sake of the simplicity
   */
  private void addFunctionVariables(final ASTOdeDeclaration astOdeDeclaration) {
    for (final ASTOdeFunction astOdeAlias:astOdeDeclaration.getOdeFunctions()) {
      final VariableSymbol var = new VariableSymbol(astOdeAlias.getVariableName());
      var.setAstNode(astOdeAlias);
      final String typeName =  computeTypeName(astOdeAlias.getDatatype());
      Optional<TypeSymbol> type = PredefinedTypes.getTypeIfExists(typeName);

      var.setType(type.get());
      var.setRecordable(astOdeAlias.isRecordable());
      var.setFunction(true);
      var.setDeclaringExpression(astOdeAlias.getExpr());

      var.setBlockType(VariableSymbol.BlockType.EQUATION);

      addToScopeAndLinkWithNode(var, astOdeAlias);

      trace("Adds new variable '" + var.getFullName() + "'.", LOGGER_NAME);
    }
  }

  /**
   * Adds a variable that results from a right hand side an ODE: e.g. g_I'' -> g_I' is the new variable.
   * The corresponding ODE is added in {@code addOdeToVariable}
   *
   */
  private void addDerivedVariable(final ASTEquation ode) {
    checkState(currentScope().isPresent());
    final String variableName = getNameOfLHS(ode);
    final String originalVarName = ode.getLhs().getName().toString(); //name of the original variable e.g. no trailing '

    final Optional<VariableSymbol> originalSymbol = currentScope().get().resolve(originalVarName,VariableSymbol.KIND);
    if (originalSymbol.isPresent()) {
      final TypeSymbol originalType = originalSymbol.get().getType();
      UnitRepresentation derivedUnit = UnitRepresentation.getBuilder().serialization(originalType.getName()).
          ignoreMagnitude(true).build().deriveT(ode.getLhs().getDifferentialOrder().size() - 1);
      final TypeSymbol derivedType = PredefinedTypes.getType(derivedUnit.serialize());

      final VariableSymbol var = new VariableSymbol(variableName);

      var.setAstNode(ode.getLhs());
      var.setType(derivedType);
      var.setRecordable(true);
      var.setFunction(false);

      var.setBlockType(VariableSymbol.BlockType.STATE);

      addToScopeAndLinkWithNode(var, ode);

      trace("Add new variable derived from the ODE: '" + var.getFullName() + "'.", LOGGER_NAME);
    }
    else {
      Log.warn(LOGGER_NAME + ": " + String.format("The state %s variable is undefined", originalVarName));
    }
  }

  private void assignOdeToVariables(final ASTOdeDeclaration astOdeDeclaration) {
      astOdeDeclaration
          .getODEs()
          .forEach(this::addOdeToVariable);

  }

  private void addOdeToVariable(final ASTEquation ode) {
    checkState(this.currentScope().isPresent());
    final Scope scope = currentScope().get();
    if (ode.getLhs().getDifferentialOrder().size() > 0) {
      final String variableName = getNameOfLHS(ode.getLhs());
      final Optional<VariableSymbol> stateVariable = scope.resolve(variableName, VariableSymbol.KIND);

      if (stateVariable.isPresent()) {
        stateVariable.get().setOdeDeclaration(ode.getRhs());
      }
      else {
        Log.warn("NESTMLSymbolTableCreator: The left side of the ode is undefined. Cannot assign its definition: " + variableName, ode.get_SourcePositionStart());
      }
    }
    else {
      Log.warn("NESTMLSymbolTableCreator: The lefthandside of an equation must be a derivative, e.g. " + ode.getLhs().toString() + "'", ode.get_SourcePositionStart());
    }


  }

  /**
   * For each buffer, if it is used in the Cond_sum function, a conductance flag is added. E.g. in
   * equations:
   *   V_m = Cond_sum(GI, spikes)
   * end
   * input:
   *   spikes <- spike
   * end
   *
   * spikes buffer is marked conductanceBased
   */
  private void markConductanceBasedBuffers(final ASTOdeDeclaration astOdeDeclaration, List<ASTInputLine> inputLines) {
    checkState(currentScope().isPresent());

    if (!inputLines.isEmpty()) {

      final Collection<VariableSymbol> bufferSymbols = currentScope().get().resolveLocally(VariableSymbol.KIND);

      final Collection<VariableSymbol> spikeBuffers = bufferSymbols
          .stream()
          .filter(VariableSymbol::isSpikeBuffer)
          .collect(Collectors.toList());
      final List<ASTNode> equations = Lists.newArrayList();
      equations.addAll(astOdeDeclaration.getODEs());
      equations.addAll(astOdeDeclaration.getOdeFunctions());

      for (VariableSymbol spikeBuffer:spikeBuffers) {
        final Optional<?> bufferInCondSumCall = equations
            .stream()
            .flatMap(astEquation -> getCondSumFunctionCall(astEquation).stream())
            // that there is one parameter which is the simple name is granted by cocos
            .map(astFunctionCall -> astFunctionCall.getArgs().get(1).getVariable().get())
            .filter(variable -> variable.getName().toString().equals(spikeBuffer.getName()))
            .findAny();

        bufferInCondSumCall.ifPresent(o -> spikeBuffer.setConductanceBased(true));

      }

    }

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
   * function V_m mV[testSize] = y3 + E_L
   * }
   */
  public void visit(final ASTInputLine inputLineAst) {
    checkState(this.currentScope().isPresent());
    checkState(currentTypeSymbol.isPresent());

    final TypeSymbol bufferType = PredefinedTypes.getBufferType();

    final VariableSymbol var = new VariableSymbol(inputLineAst.getName());

    var.setType(bufferType);

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
    varBlock = of(astVarBlock);
  }

  @Override
  public void endVisit(final ASTVar_Block astVarBlock) {
    varBlock = empty();
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

  @Override
  public void visit(final ASTDeclaration astDeclaration) {
    checkState(currentTypeSymbol.isPresent());

    if (this.varBlock.isPresent()) {

      if (varBlock.get().isState()) {
        addVariablesFromDeclaration(
            astDeclaration,
            STATE);
      }
      else if (varBlock.get().isParameters ()) {
        addVariablesFromDeclaration(
            astDeclaration,
            VariableSymbol.BlockType.PARAMETERS);
      }
      else if (varBlock.get().isInternals()) {
        addVariablesFromDeclaration(
            astDeclaration,
            VariableSymbol.BlockType.INTERNALS);
      }
      else {
        addVariablesFromDeclaration(
            astDeclaration,
            VariableSymbol.BlockType.LOCAL);
      }

    }
    else { // the declaration is defined inside a method
      addVariablesFromDeclaration(
          astDeclaration,
          VariableSymbol.BlockType.LOCAL);

    }

  }

  /**
   * Adds variables from a declaration. Distinguishes between the place of the declaration, e.g.
   * local, state, ...
   */
  private void addVariablesFromDeclaration(
      final ASTDeclaration astDeclaration,
      final VariableSymbol.BlockType blockType) {

    for (String varName : astDeclaration.getVars()) { // multiple vars in one decl possible

      final VariableSymbol var = new VariableSymbol(varName);
      var.setAstNode(astDeclaration);
      final String typeName =  computeTypeName(astDeclaration.getDatatype());
      var.setType(PredefinedTypes.getType(typeName));

      boolean isRecordableVariable = blockType == STATE || astDeclaration.isRecordable();

      if (isRecordableVariable) {
        // otherwise is set to false.
        var.setRecordable(true);
      }

      if (astDeclaration.isFunction()) {
        var.setFunction(true);
      }

      if (astDeclaration.getExpr().isPresent()) {
        var.setDeclaringExpression(astDeclaration.getExpr().get());
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
    var.setRecordable(true);
    var.setFunction(false);
    var.setDeclaringExpression(astShape.getRhs());
    var.setBlockType(VariableSymbol.BlockType.SHAPE);

    addToScopeAndLinkWithNode(var, astShape);

    trace("Adds new shape variable '" + var.getFullName() + "'.", LOGGER_NAME);
  }

}
