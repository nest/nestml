package org.nest.units._visitor;

import de.monticore.symboltable.Scope;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTOdeFunction;
import org.nest.ode._ast.ASTShape;
import org.nest.symboltable.NestmlSymbols;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import java.util.Optional;

import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * Visitor to ODE Shape and Equation nodes. Calculates implicit type and updates Symbol table.
 * To be called as soon as symbol table is created.
 *
 * @author ptraeder
 */
public class ODEPostProcessingVisitor implements NESTMLVisitor {

  private static final String ERROR_CODE = "NESTML_ODEPostProcessingVisitor";

  public void visit(ASTShape astShape) {
    if (astShape.getRhs().getType().isError()) {
      warn(ERROR_CODE + ": Error in Expression type calculation: " + astShape.getRhs().getType().getError(), astShape.get_SourcePositionStart());
    }
    //TODO: find out what needs to be done here

  }


  public void visit(ASTEquation astEquation) {
    if (astEquation.getRhs().getType().isError()) {
      warn(ERROR_CODE + ": Error in Expression type calculation: " + astEquation.getRhs().getType().getError(), astEquation.get_SourcePositionStart());

      return;
    }
    if (!astEquation.getEnclosingScope().isPresent()) {
      warn(ERROR_CODE + "Enclosing scope not present. Run ScopeCreator", astEquation.get_SourcePositionStart());
      return;
    }

    //Resolve LHS Variable
    String varName = astEquation.getLhs().getSimpleName();
    Scope enclosingScope = astEquation.getEnclosingScope().get();
    Optional<VariableSymbol> varSymbol = NestmlSymbols.resolve(varName, enclosingScope);

    TypeSymbol varType;
    if (!varSymbol.isPresent()) {
      warn(ERROR_CODE + " Error while resolving the variable to be derived in ODE: " + varName, astEquation.get_SourcePositionStart());
      return;
    }
    //Derive varType
    varType = varSymbol.get().getType();

    if (varType.getType() != TypeSymbol.Type.UNIT &&
        varType != getRealType()) {
      warn(ERROR_CODE + "Type of LHS Variable in ODE is neither a Unit nor real at: " + astEquation.get_SourcePositionStart() + ". Skipping.", astEquation.get_SourcePositionStart());
      return;
    }

    UnitRepresentation varUnit = UnitRepresentation.getBuilder().serialization(varType.getName()).build();
    UnitRepresentation derivedVarUnit = varUnit.deriveT(astEquation.getLhs().getDifferentialOrder().size());

    //get type of RHS expression
    TypeSymbol typeFromExpression = astEquation.getRhs().getType().getValue();

    if (typeFromExpression.getType() != TypeSymbol.Type.UNIT &&
        typeFromExpression != getRealType()) {
      warn(ERROR_CODE + "Type of ODE is neither a Unit nor real ", astEquation.get_SourcePositionStart());
      return;
    }
    UnitRepresentation unitFromExpression = UnitRepresentation.getBuilder().serialization(typeFromExpression.getName()).build();
    //set any of the units to ignoreMagnitude
    unitFromExpression.setIgnoreMagnitude(true);
    //do the actual test:
    if (!unitFromExpression.equals(derivedVarUnit)) {
      //remove magnitude for clearer error message
      derivedVarUnit.setMagnitude(0);
      unitFromExpression.setMagnitude(0);
      warn(ERROR_CODE + "Type of (derived) variable " + astEquation.getLhs().toString() + " is: " + derivedVarUnit.prettyPrint() +
           ". This does not match Type of RHS expression: " + unitFromExpression.prettyPrint(), astEquation.get_SourcePositionStart());
    }
  }

  @Override
  public void traverse(org.nest.ode._ast.ASTOdeDeclaration node) {
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
