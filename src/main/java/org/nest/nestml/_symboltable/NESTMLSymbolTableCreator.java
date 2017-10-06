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
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.nestml._visitor.UnitsSIVisitor;
import org.nest.utils.AstUtils;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.trace;
import static java.util.Objects.requireNonNull;
import static java.util.Optional.empty;
import static java.util.Optional.of;
import static org.nest.nestml._symboltable.symbols.NeuronSymbol.Type.NEURON;
import static org.nest.nestml._symboltable.symbols.VariableSymbol.BlockType.*;
import static org.nest.nestml._symboltable.symbols.VariableSymbol.VariableType.*;
import static org.nest.utils.AstUtils.computeTypeName;

/**
 * Creates NESTML symbols.
 *
 * @author plotnikov
 */
public class NESTMLSymbolTableCreator extends CommonSymbolTableCreator implements NESTMLVisitor {
  private static String LOGGER_NAME = "NESTML_SymbolTableCreator";
  private Optional<NeuronSymbol> currentTypeSymbol = empty();
  private Optional<ASTBlockWithVariables> varBlock = empty();

  public NESTMLSymbolTableCreator(
      final ResolvingConfiguration resolvingConfiguration,
      final MutableScope enclosingScope) {
    super(resolvingConfiguration, enclosingScope);
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
    // TODO must return an optional
    return getFirstCreatedScope();
  }


  public void visit(final ASTNESTMLCompilationUnit compilationUnitAst) {

    final MutableScope artifactScope = new ArtifactScope(
        empty(),
        compilationUnitAst.getArtifactName(),
        Lists.newArrayList());
    putOnStack(artifactScope);

    final String msg = "Adds an artifact scope for the NESTML model file: " + compilationUnitAst.getArtifactName();
    trace(msg, LOGGER_NAME);
  }


  public void endVisit(final ASTNESTMLCompilationUnit compilationUnitAst) {
    removeCurrentScope();
    setEnclosingScopeOfNodes(compilationUnitAst);
    final String msg = "Finishes handling and sets scopes on all ASTs for the artifact: " +
        compilationUnitAst.getArtifactName();
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

    if (astNeuron.findEquationsBlock().isPresent()) {
      addFunctionVariables(astNeuron.findEquationsBlock().get());
    }

    // new variable from the ODE block could be added. Check, whether they don't clutter with existing one
    final NestmlCoCosManager nestmlCoCosManager = new NestmlCoCosManager();

    final List<Finding> undefinedVariables = nestmlCoCosManager.checkThatVariableDefinedAtLeastOnce(astNeuron);

    if (undefinedVariables.isEmpty()) {
      final List<Finding> undefinedMethods = nestmlCoCosManager.checkThatMethodDefinedAtLeastOnce(astNeuron);

      if (undefinedMethods.isEmpty()) {
        final List<Finding> multipleDefinitions = nestmlCoCosManager.checkThatElementDefinedAtMostOnce(astNeuron);
        if (multipleDefinitions.isEmpty()) {
          if (astNeuron.findEquationsBlock().isPresent()) {

              connectOdesToInitialValues(astNeuron.findEquationsBlock().get());
              markConductanceBasedBuffers(astNeuron.findEquationsBlock().get(), astNeuron.getInputLines());
          }

        }
        else {
          final String msg = LOGGER_NAME + " : Cannot correctly build the symboltable, at least one variable is " +
                             "defined multiple. See error log.";
          Log.error(msg);
        }
      }
      else {
        final String msg = LOGGER_NAME + " : Cannot correctly build the symboltable, at least one method is " +
                           "undefined. See error log.";
        Log.error(msg);
      }

    }
    else {
      final String msg = LOGGER_NAME + " : Cannot correctly build the symboltable, at least one variable is " +
                         "undefined. See error log.";
      Log.error(msg);
    }

    removeCurrentScope();
    currentTypeSymbol = empty();
  }

  /**
   * Analyzes the ode block and add all aliases. E.g.:
   *   equations:
   *      I_syn pA = I_exc - I_inh # <- inplace function
   *      V_m mV = I_syn / 1 ms
   *   end
   * Results in an additional variable for G' (first equations G''). For the sake of the simplicity
   */
  private void addFunctionVariables(final ASTEquationsBlock astOdeDeclaration) {
    for (final ASTOdeFunction astOdeAlias:astOdeDeclaration.getOdeFunctions()) {
      final VariableSymbol var = new VariableSymbol(astOdeAlias.getVariableName(), EQUATIONS, VARIABLE);
      var.setAstNode(astOdeAlias);
      final String typeName =  computeTypeName(astOdeAlias.getDatatype());
      Optional<TypeSymbol> type = PredefinedTypes.getTypeIfExists(typeName);

      var.setType(type.get());
      var.setRecordable(astOdeAlias.isRecordable());
      var.setFunction(true);
      var.setDeclaringExpression(astOdeAlias.getExpr());

      addToScopeAndLinkWithNode(var, astOdeAlias);

      trace("Adds new variable '" + var.getFullName() + "'.", LOGGER_NAME);
    }
  }

  private void connectOdesToInitialValues(final ASTEquationsBlock astOdeDeclaration) {
      astOdeDeclaration.getEquations().forEach(equation -> connectOdeToVariable(equation.getLhs(), equation.getRhs()));

      astOdeDeclaration.getShapes()
          .stream()
          .filter(astShape -> astShape.getLhs().getDifferentialOrder().size() > 0)
          .forEach(astShape -> connectOdeToVariable(astShape.getLhs(), astShape.getRhs()));

      astOdeDeclaration.getShapes()
          .stream()
          .map(ASTShape::getLhs)
          .forEach(this::markShapeVariables);
  }

  private void connectOdeToVariable(final ASTDerivative derivedVariable, final ASTExpr astExpr) {
    checkState(this.currentScope().isPresent());
    final Scope scope = currentScope().get();
    final String variableName = derivedVariable.getNameOfDerivedVariable();
    final Optional<VariableSymbol> variable = scope.resolve(variableName, VariableSymbol.KIND);

    if (variable.isPresent()) {
      variable.get().setOdeDeclaration(astExpr);
    }
    else {
      Log.warn("NESTMLSymbolTableCreator: The left side of the ode is undefined. Cannot assign its definition: " +
               variableName, derivedVariable.get_SourcePositionStart());
    }

  }

  private void markShapeVariables(final ASTDerivative derivedVariable) {
    checkState(this.currentScope().isPresent());
    final Scope scope = currentScope().get();
    final String variableName = derivedVariable.getNameOfDerivedVariable();
    final Optional<VariableSymbol> variable = scope.resolve(variableName, VariableSymbol.KIND);

    if (variable.isPresent()) {
      variable.get().markShape();
    }
    else {
      Log.warn("NESTMLSymbolTableCreator: The left side of the ode is undefined. Cannot assign its definition: " +
               variableName, derivedVariable.get_SourcePositionStart());
    }

  }
  /**
   * For each buffer of type nS, a conductance flag is added. E.g. in
   * equations:
   *   V_m = convolve(GI, spikes)
   * end
   * input:
   *   spikes nS <- spike
   * end
   *
   * spikes buffer is marked conductanceBased
   */
  private void markConductanceBasedBuffers(final ASTEquationsBlock astOdeDeclaration, List<ASTInputLine> inputLines) {
    checkState(currentScope().isPresent());

    if (!inputLines.isEmpty()) {

      final Collection<VariableSymbol> allVariables = currentScope().get().resolveLocally(VariableSymbol.KIND);

      final Collection<VariableSymbol> spikeBuffers = allVariables
          .stream()
          .filter(VariableSymbol::isSpikeBuffer)
          .collect(Collectors.toList());

      for(VariableSymbol spikeBuffer : spikeBuffers) {
        if (spikeBuffer.getType().getName().equals(UnitRepresentation.lookupName("nS").get().serialize())) {
          spikeBuffer.setConductanceBased(true);
        }

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
    final VariableSymbol var = new VariableSymbol(inputLineAst.getName(), INPUT, BUFFER);

    //manually set datatype for current buffers and run UnitsVisitor to produce coherent state:
    if(inputLineAst.isCurrent()){
      ASTUnitType pAType = ASTUnitType.getBuilder().unit("pA").build();
      inputLineAst.setDatatype(ASTDatatype.getBuilder().unitType(pAType).build());
      UnitsSIVisitor.convertSiUnitsToSignature(inputLineAst);
    }

    //parser complains before we get here if datatypes are not set as expected:
    TypeSymbol bufferType = PredefinedTypes.getType(AstUtils.computeTypeName(inputLineAst.getDatatype().get()));
    //mark the typeSymbol as a buffer
    bufferType.setBufferType(true);
    var.setType(bufferType);


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
    for (ASTParameter p : funcAst.getParameters()) {
      String typeName = computeTypeName(p.getDatatype());
      Optional<TypeSymbol> type = PredefinedTypes.getTypeIfExists(typeName);

      checkState(type.isPresent());

      methodSymbol.addParameterType(type.get());

      // add a var entry for method body
      VariableSymbol var = new VariableSymbol(p.getName(), LOCAL, VARIABLE);
      var.setAstNode(p);
      var.setType(type.get());

      addToScopeAndLinkWithNode(var, p);

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

  public void visit(final ASTUpdateBlock dynamicsAst) {
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
  public void endVisit(final ASTUpdateBlock astUpdateBlock) {
    removeCurrentScope();
  }

  @Override
  public void visit(final ASTBlockWithVariables astVarBlock) {
    varBlock = of(astVarBlock);
  }

  @Override
  public void endVisit(final ASTBlockWithVariables astVarBlock) {
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
        addVariablesFromDeclaration(astDeclaration, STATE);
      }
      else if (varBlock.get().isParameters()) {
        addVariablesFromDeclaration(astDeclaration, VariableSymbol.BlockType.PARAMETERS);
      }
      else if (varBlock.get().isInternals()) {
        addVariablesFromDeclaration(astDeclaration, VariableSymbol.BlockType.INTERNALS);
      }
      else if (varBlock.get().isInitial_values()) {
        addVariablesFromDeclaration(astDeclaration, VariableSymbol.BlockType.INITIAL_VALUES);
      }
      else {
        checkState(false, "This branch is by grammar construction unreachable.");
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
  private void addVariablesFromDeclaration(final ASTDeclaration astDeclaration,
                                           final VariableSymbol.BlockType blockType) {

    for (final ASTVariable variable : astDeclaration.getVars()) { // multiple vars in one decl possible

      final VariableSymbol var = new VariableSymbol(variable.toString(), blockType, VARIABLE);
      var.setAstNode(astDeclaration);
      final String typeName =  computeTypeName(astDeclaration.getDatatype());
      var.setType(PredefinedTypes.getType(typeName));

      boolean isRecordableVariable = blockType == STATE || blockType == INITIAL_VALUES || astDeclaration.isRecordable();
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

      addToScopeAndLinkWithNode(var, astDeclaration);

      trace("Adds new variable: " + var.getName(), LOGGER_NAME);

    }

  }

  @Override
  public void visit(final ASTShape astShape) {
    // in this case the shape is defined is a function. no initialvalues are necessary
    if (astShape.getLhs().getDifferentialOrder().size() == 0) {
      final TypeSymbol type = PredefinedTypes.getType("real");
      final VariableSymbol var = new VariableSymbol(astShape.getLhs().toString(), EQUATIONS, SHAPE);

      var.setAstNode(astShape);
      var.setType(type);
      var.setRecordable(false);
      var.setFunction(false);
      var.setDeclaringExpression(astShape.getRhs());

      addToScopeAndLinkWithNode(var, astShape);

      trace("Adds new shape variable '" + var.getFullName() + "'.", LOGGER_NAME);
    }

  }

}
