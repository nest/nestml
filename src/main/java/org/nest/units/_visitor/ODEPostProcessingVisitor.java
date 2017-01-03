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

import java.util.Iterator;
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
    if(astShape.getRhs().getType().isError()){
      warn(ERROR_CODE + ": Error in Expression type calculation: " + astShape.getRhs().getType().getError());

      return;
    }
    //TODO: find out what needs to be done here

  }


  public void visit(ASTEquation astEquation) {
    if(astEquation.getRhs().getType().isError()){
      warn(ERROR_CODE + ": Error in Expression type calculation: " + astEquation.getRhs().getType().getError());

      return;
    }
    if(!astEquation.getEnclosingScope().isPresent()){
      warn(ERROR_CODE +"Enclosing scope not present. Run ScopeCreator");
      return;
    }

    //Resolve LHS Variable
    String varName = astEquation.getLhs().getSimpleName();
    Scope enclosingScope = astEquation.getEnclosingScope().get();
    Optional<VariableSymbol> varSymbol = NestmlSymbols.resolve(varName,enclosingScope);

    TypeSymbol varType;
    if(!varSymbol.isPresent()){
      warn(ERROR_CODE +" Error while resolving the variable to be derived in ODE: " + varName);
      return;
    }
    //Derive varType
    varType = varSymbol.get().getType();

    if(varType.getType() != TypeSymbol.Type.UNIT &&
        varType != getRealType()){
      warn(ERROR_CODE+ "Type of LHS Variable in ODE is neither a Unit nor real at: "+astEquation.get_SourcePositionStart()+". Skipping.");
      return;
    }

    UnitRepresentation varUnit = new UnitRepresentation(varType.getName());
    UnitRepresentation derivedVarUnit = varUnit.deriveT(astEquation.getLhs().getDifferentialOrder().size());

    //get type of RHS expression
    TypeSymbol typeFromExpression = astEquation.getRhs().getType().getValue();

    if(typeFromExpression.getType() != TypeSymbol.Type.UNIT &&
        typeFromExpression != getRealType()) {
      warn(ERROR_CODE+ "Type of ODE is neither a Unit nor real at: "+astEquation.get_SourcePositionStart());
      return;
    }
    UnitRepresentation unitFromExpression = new UnitRepresentation(typeFromExpression.getName());
    //set any of the units to ignoreMagnitude
    unitFromExpression.setIgnoreMagnitude(true);
    //do the actual test:
    if(!unitFromExpression.equals(derivedVarUnit)){
      //remove magnitude for clearer error message
      derivedVarUnit.setMagnitude(0);
      unitFromExpression.setMagnitude(0);
      warn(ERROR_CODE+ "Type of (derived) variable "+ astEquation.getLhs().toString() + " is: "+ derivedVarUnit.prettyPrint()+
          ". This does not match Type of RHS expression: "+unitFromExpression.prettyPrint()+
          " at: " +astEquation.get_SourcePositionStart()+". Magnitudes are ignored in ODE Expressions" );
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
      Iterator<ASTOdeFunction> iter_oDEAliass = node.getOdeFunctions().iterator();
      while (iter_oDEAliass.hasNext()) {
        iter_oDEAliass.next().accept(getRealThis());
      }
    }
  }
}
