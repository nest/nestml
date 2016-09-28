package org.nest.units._visitor;

import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTShape;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import java.util.Iterator;

import static de.se_rwth.commons.logging.Log.warn;

/**
 * Visitor to ODE Shape and Equation nodes. Calculates implicit type and updates Symbol table.
 * To be called as soon as symbol table is created.
 *
 * @author ptraeder
 */
public class ODEPostProcessingVisitor implements NESTMLVisitor {

  private static final String ERROR_CODE = "NESTML_ODEPostProcessingVisitor";

  public void visit(ASTShape astShape) {
    if(astShape.getRhs().computeType().get().isError()){
      warn(ERROR_CODE + ": Error in Expression type calculation: " + astShape.getRhs().getType().get().getError());

      return;
    }
    final TypeSymbol type = astShape.getRhs().getType().get().getValue();

    if(astShape.getSymbol().isPresent()){
      final VariableSymbol var = (VariableSymbol) astShape.getSymbol().get();
      var.setType(type);
    }
  }


  public void visit(ASTEquation astEquation) {
    if(astEquation.getRhs().computeType().get().isError()){
      warn(ERROR_CODE + ": Error in Expression type calculation: " + astEquation.getRhs().getType().get().getError());
      return;
    }

    //TODO: Test if implicit types of expression and derivation from original type match?

    //Calculate type implicit from expression:
    UnitRepresentation derivativeUnit = new UnitRepresentation(0,0,0,0,0,0,0,0);
    TypeSymbol typeFromExpression = astEquation.getRhs().getType().get().getValue();
    if(typeFromExpression.getType() == TypeSymbol.Type.UNIT){
      derivativeUnit = new UnitRepresentation(typeFromExpression.getName());
    }
    derivativeUnit = derivativeUnit.deriveT(astEquation.getLhs().getDifferentialOrder().size());
    typeFromExpression = PredefinedTypes.getType(derivativeUnit.serialize());

    if(astEquation.getSymbol().isPresent()){
    final VariableSymbol var = (VariableSymbol) astEquation.getSymbol().get();
      var.setType(typeFromExpression);
    }
  }

  @Override
  public void traverse(org.nest.ode._ast.ASTOdeDeclaration node) {
    //TODO: Find a sensible hierarchy for shapes,equations and aliases.
    {
      Iterator<org.nest.ode._ast.ASTShape> iter_shapes = node.getShapes().iterator();
      while (iter_shapes.hasNext()) {
        iter_shapes.next().accept(getRealThis());
      }
    }

    {
      Iterator<org.nest.ode._ast.ASTEquation> iter_equations = node.getEquations().iterator();
      while (iter_equations.hasNext()) {
        iter_equations.next().accept(getRealThis());
      }
    }

    {
      Iterator<org.nest.ode._ast.ASTODEAlias> iter_oDEAliass = node.getODEAliass().iterator();
      while (iter_oDEAliass.hasNext()) {
        iter_oDEAliass.next().accept(getRealThis());
      }
    }
  }
}
