/*
 * ODEPostProcessingVisitor.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.nest.nestml._visitor;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTOdeDeclaration;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTOdeFunction;
import org.nest.nestml._ast.ASTShape;
import org.nest.nestml._symboltable.NestmlSymbols;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Finding.error;
import static de.se_rwth.commons.logging.Log.trace;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.getRealType;

/**
 * Visitor of Shape and Equation nodes. Calculates implicit type and updates Symbol table.
 * This visitor can be called, after the symbol table for the neuron is already built. E.g. in the endVisit(ASTNeuron n)
 * method.
 *
 * @author ptraeder
 */
public class ODEPostProcessingVisitor implements NESTMLVisitor {

  public void visit(final ASTShape astShape) {
    if (astShape.getRhs().getType().isError()) {
      warn(NestmlErrorStrings.expressionCalculation(
          this,
          astShape.getRhs().getType().getError()),
          astShape.get_SourcePositionStart());
    }

    trace("Find out what needs to be done here", getClass().getSimpleName());
  }


  public void visit(final ASTEquation astEquation) {
    if (astEquation.getRhs().getType().isError()) {
      warn(NestmlErrorStrings.expressionCalculation(this, astEquation.getRhs().getType().getError()), astEquation.get_SourcePositionStart());
      return;
    }
    if (!astEquation.getEnclosingScope().isPresent()) {
      trace("Enclosing scope not present. Run ScopeCreator", getClass().getSimpleName());
      return;
    }

    //Resolve LHS Variable
    String varName = astEquation.getLhs().getSimpleName();
    Scope enclosingScope = astEquation.getEnclosingScope().get();
    Optional<VariableSymbol> varSymbol = NestmlSymbols.resolve(varName, enclosingScope);

    TypeSymbol varType;
    checkState(varSymbol.isPresent(), " Error while resolving the variable to be derived in ODE: " + varName);
    //Derive varType
    varType = varSymbol.get().getType();

    if (varType.getType() != TypeSymbol.Type.UNIT &&
        !varType.equals(getRealType()) ) {
      error(NestmlErrorStrings.expressionNonNumeric(this), astEquation.get_SourcePositionStart());
      return;
    }

    UnitRepresentation varUnit = UnitRepresentation.getBuilder().serialization(varType.getName()).build();
    UnitRepresentation derivedVarUnit = varUnit.deriveT(astEquation.getLhs().getDifferentialOrder().size());

    //get type of RHS expression
    TypeSymbol typeFromExpression = astEquation.getRhs().getType().getValue();

    if (typeFromExpression.getType() != TypeSymbol.Type.UNIT &&
        !typeFromExpression.equals(getRealType()) ) {
      error(NestmlErrorStrings.expressionNonNumeric(this), astEquation.get_SourcePositionStart());
      return;
    }
    UnitRepresentation unitFromExpression = UnitRepresentation.getBuilder().serialization(typeFromExpression.getName()).build();
    //set any of the units to ignoreMagnitude
    unitFromExpression.setIgnoreMagnitude(false);
    //do the actual test:
    if (!unitFromExpression.equals(derivedVarUnit)) {
      //remove magnitude for clearer error message

      //derivedVarUnit.setMagnitude(0);
      //unitFromExpression.setMagnitude(0);
      final String msg = NestmlErrorStrings.expressionMissmatch(
          this,
          astEquation.getLhs().toString(),
          derivedVarUnit.prettyPrint(),
          unitFromExpression.prettyPrint());
      warn(msg, astEquation.get_SourcePositionStart());
    }

  }

  @Override
  public void traverse(ASTOdeDeclaration node) {
    //TODO: Find a sensible hierarchy for shapes,equations and aliases.
    for (ASTShape astShape : node.getShapes()) {
      astShape.accept(getRealThis());
    }
    for (ASTEquation astEquation : node.getEquations()) {
      astEquation.accept(getRealThis());
    }
    for (ASTOdeFunction astOdeFunction : node.getOdeFunctions()) {
      astOdeFunction.accept(getRealThis());
    }

  }

}
