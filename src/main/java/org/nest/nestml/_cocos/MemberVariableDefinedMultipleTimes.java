/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import com.google.common.collect.Maps;
import de.monticore.ast.ASTNode;
import de.se_rwth.commons.SourcePosition;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTVariable;
import org.nest.utils.AstUtils;

import java.util.Map;

import static de.se_rwth.commons.logging.Log.error;

/**
 * This context condition checks, whether the state/parameter/internal-variables
 * of a component/neuron is not defined multiple times.
 *
 * E.g. in the following case x defined twice and results in an error
 * neuron NeuronInTest:
 *   state: x mV end
 *   parameters: x real end
 * end
 *
 * @author ippen, plotnikov
 */
public class MemberVariableDefinedMultipleTimes implements NESTMLASTNeuronCoCo {

  @Override
  public void check(ASTNeuron neuron) {
    check(neuron.getBody());
  }

  private void check(ASTBody body) {
    Map<String, SourcePosition> varNames = Maps.newHashMap();
    body.getStateDeclarations().forEach(declaration -> addNames(varNames, declaration));
    body.getParameterDeclarations().forEach(declaration -> addNames(varNames, declaration));
    body.getInternalDeclarations().forEach(declaration -> addNames(varNames, declaration));
    body.getODEAliases().forEach(odeAlias -> addName(varNames, odeAlias.getName(), odeAlias.getAstNode().get()));
    body.getInputLines().forEach(inputLine -> addVariable(inputLine.getName().get(), varNames, inputLine) );
    body.getShapes().forEach(astShape -> addVariable(AstUtils.getNameOfLHS(astShape), varNames, astShape));
  }

  private void addNames(final Map<String, SourcePosition> names, final ASTDeclaration decl) {
    for (final ASTVariable variable : decl.getVars()) {
      addVariable(variable.toString(), names, decl);
    }

  }

  private void addName(
      final Map<String, SourcePosition> names,
      final String variableName,
      final ASTNode decl) {
    addVariable(variableName, names, decl);

  }

  private void addVariable(
      final String var,
      final Map<String, SourcePosition> names,
      final ASTNode astNode) {
    if (names.containsKey(var)) {
      final String msg = NestmlErrorStrings.message(this,var,
              names.get(var).getLine(),
              names.get(var).getColumn());

     error(msg, astNode.get_SourcePositionStart());

    }
    else {
      names.put(var, astNode.get_SourcePositionStart());
    }

  }

}
