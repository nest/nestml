/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import de.se_rwth.commons.logging.Log;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * Helper routine to calculate the category of the particular type.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class TypeChecker {
  private final PredefinedTypesFactory predefinedTypesFactory;

  public TypeChecker(PredefinedTypesFactory predefinedTypesFactory) {
    this.predefinedTypesFactory = predefinedTypesFactory;
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
  public boolean checkInteger(final TypeSymbol u) {
    if (u != null) {
      return u.getName().equals(predefinedTypesFactory.getIntegerType().getName());
    }
    return false;
  }

  /**
   * Checks that the {@code type} is an {@code real}.
   */
  public boolean checkReal(final TypeSymbol u) {
    if (u != null) {
      return u.getName().equals(predefinedTypesFactory.getRealType().getName());
    }
    return false;
  }

  public boolean checkVoid(final TypeSymbol type) {
    if (type != null) {
      return type.getName().equals(predefinedTypesFactory.getVoidType().getName());
    }
    return false;
  }

  public boolean checkString(final TypeSymbol type) {
    if (type != null) {
      return type.getName().equals(predefinedTypesFactory.getStringType().getName());
    }
    return false;
  }

  public boolean checkBoolean(final TypeSymbol type) {
    if (type != null) {
      return type.getName().equals(predefinedTypesFactory.getBooleanType().getName());
    }
    return false;
  }

  public boolean checkUnit(final TypeSymbol rType) {
    Log.warn("!!!!!!!! boolean checkUnit(TypeSymbol rType) unimplemented: " + rType);
    return false;
  }

}
