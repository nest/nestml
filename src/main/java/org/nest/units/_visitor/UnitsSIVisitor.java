/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units._visitor;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTNESTMLNumericLiteral;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.spl._ast.ASTSPLNode;
import org.nest.units._ast.ASTUnitType;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.units.unitrepresentation.UnitTranslator;
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
  public static List<Finding> convertSiUnitsToSignature(final ASTSPLNode compilationUnit) {
    final UnitsSIVisitor unitsSIVisitor = new UnitsSIVisitor();
    compilationUnit.accept(unitsSIVisitor);
    final List<Finding> findings = LogHelper.getModelFindings(Log.getFindings());
    return findings;
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
   * Verify that the given Unit is valid. Use TranslationVisitor to generate serialization of Unit.
   * Overwrite the nodes' "unit" field with the serialization.
   */
  public void visit(ASTUnitType astUnitType){
    if (astUnitType.getUnit().isPresent()) {
      String unit = astUnitType.getUnit().get();
      final Optional<String> convertedUnit = translator.calculateUnitType(astUnitType);

      if (convertedUnit.isPresent()) {
        astUnitType.setUnit(convertedUnit.get());
      }
      else {
        Log.error(ERROR_CODE + "The unit " + unit + " is not an SI unit.", astUnitType.get_SourcePositionStart());
      }
    }

    final Optional<String> translatedUnit = translator.calculateUnitType(astUnitType);
    if (translatedUnit.isPresent()) {
      astUnitType.setUnit(translatedUnit.get());
    }
    else {
      Log.error(ERROR_CODE + "The unit used in the expression is not an SI unit.", astUnitType.get_SourcePositionStart());
    }

  }

  public void visit(ASTNESTMLNumericLiteral astNestmlNumericLiteral) {
    if (astNestmlNumericLiteral.getType().isPresent()) {
      final String unitName = astNestmlNumericLiteral.getType().get();
      final Optional<UnitRepresentation> unit = UnitRepresentation.lookupName(unitName);
      if (!unit.isPresent()) {
        final String msg = ERROR_CODE + "The unit used in the '" + unitName + "' literal is not an SI unit.";
        Log.error(msg, astNestmlNumericLiteral.get_SourcePositionStart());
      }

    }

  }

}
