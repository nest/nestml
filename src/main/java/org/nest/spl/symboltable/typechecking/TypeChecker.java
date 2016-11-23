/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static org.nest.symboltable.predefined.PredefinedTypes.*;
import static org.nest.symboltable.symbols.TypeSymbol.Type.UNIT;

/**
 * Helper routine to calculate the category of the particular type.
 *
 * @author plotnikov
 */
public class TypeChecker {
  public static boolean  isCompatible(final String lhsType, final String rhsType) {
    return isCompatible(getType(lhsType), getType(rhsType));
  }

  public static boolean  isCompatible(final TypeSymbol lhsType, final TypeSymbol rhsType) {

    //simplified check for Units set to ignore magnitude: (ignore if any is set)
    if(lhsType.getType().equals(UNIT) && rhsType.getType().equals(UNIT)){
      UnitRepresentation lhsUnit = new UnitRepresentation(lhsType.getName());
      UnitRepresentation rhsUnit = new UnitRepresentation(rhsType.getName());
      return lhsUnit.equals(rhsUnit);
    }

    if (lhsType.equals(rhsType)) {
      return true;
    }
    if (lhsType.equals(getRealType()) &&
        rhsType.equals(getIntegerType())) {
      return true;
    }
    if (rhsType.equals(getIntegerType()) && lhsType.getType().equals(UNIT)) {
      return true;
    }
    if (lhsType.equals(getRealType()) && rhsType.getType().equals(UNIT) ||
        rhsType.equals(getRealType()) && lhsType.getType().equals(UNIT)) {
      return true;
    }

    return false;
  }
  /**
   * Checks that the {@code type} is a numeric type {@code Integer} or {@code Real}.
   */
  public boolean checkNumber(final TypeSymbol type) {
    return checkInteger(type) || checkReal(type);
  }

  /**
   * Checks that the {@code type} is an {@code Integer}.
   */
  private boolean checkInteger(final TypeSymbol u) {
    return u != null && u.getName().equals(getIntegerType().getName());
  }

  /**
   * Checks that the {@code type} is an {@code real}.
   */
  private boolean checkReal(final TypeSymbol u) {
    return u != null && u.getName().equals(getRealType().getName());
  }

  public static boolean checkVoid(final TypeSymbol type) {
    return type != null && type.getName().equals(getVoidType().getName());
  }

  public static boolean checkString(final TypeSymbol type) {
    return type != null && type.getName().equals(getStringType().getName());

  }

  public static boolean isBoolean(final TypeSymbol type) {
    // TODO use prover equals implementation
    return type != null && type.getName().equals(getBooleanType().getName());
  }

  public static boolean checkUnit(final TypeSymbol rType) {
    //return rType.getName().equals(getUnitType().getName()); // TODO use prover equals implementation
    return rType != null && rType.getType().equals(UNIT);
  }

  public static boolean isInteger(TypeSymbol typeSymbol) {
    // TODO use prover equals implementation
    return typeSymbol != null && typeSymbol.equals(getIntegerType());
  }

}
