/*
 * UnitsSIVisitor.java
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

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTUnitType;
import org.nest.nestml._cocos.UnitsErrorStrings;
import org.nest.nestml._symboltable.unitrepresentation.SIData;
import org.nest.nestml._symboltable.unitrepresentation.UnitTranslator;
import org.nest.utils.LogHelper;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Type checking visitor for the UNITS grammar. Verifies that all units used are comprised of SI units.
 *
 * @author ptraeder
 */
public class UnitsSIVisitor implements NESTMLVisitor {
  private final static String ERROR_CODE = "NESTML_UnitsSIVisitor";
  private UnitTranslator translator = new UnitTranslator();

  /**
   * Use the static factory method: convertSiUnitsToSignature
   */
  private UnitsSIVisitor() {

  }

  /**
   * Checks that all units used in the models are well defined. In case of SI units, converts them to its signature
   * representation. In case of errors reports them as non empty return list
   * @param compilationUnit Input model to check
   * @return The list all type finding. Is emtpty iff the model doesn't contain any type issues.
   */
  public static List<Finding> convertSiUnitsToSignature(final ASTNESTMLNode compilationUnit) {
    final UnitsSIVisitor unitsSIVisitor = new UnitsSIVisitor();
    compilationUnit.accept(unitsSIVisitor);
    final Collection<Finding> findings = LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings());

    return Lists.newArrayList(findings);
  }


  /**
   * Verify that the given Unit is valid. Use UnitTranslator to generate serialization of Unit.
   * Set the nodes' "serializedUnit" field with the serialization.
   */
  public void visit(final ASTUnitType astUnitType){
    //String unit = astUnitType.getUnit().get();
    final Optional<String> convertedUnit = translator.calculateUnitType(astUnitType);

    if (convertedUnit.isPresent()) {
      astUnitType.setSerializedUnit(convertedUnit.get());
    }
    else {
      final String unit = astUnitType.unitIsPresent() ? astUnitType.getUnit().get() : astUnitType.toString();
      final String msg = UnitsErrorStrings.message(this, unit);
      Log.error(msg, astUnitType.get_SourcePositionStart());
    }

  }

  /**
   * Verify that if a literal is followed directly (only seperated by whitespaces) by a variable,
   * that the variable is one of the predefined unit variables.
   */
  public void visit(ASTExpr node) {
    if(node.numericLiteralIsPresent() && node.variableIsPresent()){
      final String varName = node.getVariable().get().toString();
      final List<String> validUnits = SIData.getCorrectSIUnits();
      boolean valid = false;

      for(String validUnit : validUnits){
        if(varName.equals(validUnit)){
          valid = true;
          break;
        }
      }

      if(!valid){
        Log.error(ERROR_CODE + varName +"is not an SI unit.", node.get_SourcePositionStart());
      }

    }
  }

}
