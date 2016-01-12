/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import de.se_rwth.commons.logging.Log;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * Helper routine to calculate the category of the particular type.
 *
 * @author plotnikov
 */
public class TypeChecker {

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
      return u.getName().equals(PredefinedTypes.getIntegerType().getName());
    }
    return false;
  }

  /**
   * Checks that the {@code type} is an {@code real}.
   */
  public boolean checkReal(final TypeSymbol u) {
    if (u != null) {
      return u.getName().equals(PredefinedTypes.getRealType().getName());
    }
    return false;
  }

  public boolean checkVoid(final TypeSymbol type) {
    if (type != null) {
      return type.getName().equals(PredefinedTypes.getVoidType().getName());
    }
    return false;
  }

  public boolean checkString(final TypeSymbol type) {
    if (type != null) {
      return type.getName().equals(PredefinedTypes.getStringType().getName());
    }
    return false;
  }

  public boolean checkBoolean(final TypeSymbol type) {
    if (type != null) {
      return type.getName().equals(PredefinedTypes.getBooleanType().getName());
    }
    return false;
  }

  public boolean checkUnit(final TypeSymbol rType) {
    Log.warn("!!!!!!!! boolean checkUnit(TypeSymbol rType) unimplemented: " + rType);
    return false;
  }

}
