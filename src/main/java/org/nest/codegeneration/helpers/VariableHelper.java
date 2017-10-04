package org.nest.codegeneration.helpers;

import org.nest.nestml._symboltable.symbols.VariableSymbol;

/**
 * Provides helper methods for the printing variables for the nest taget
 * @author plotnikov
 */
public class VariableHelper {
  static public String printOrigin(final VariableSymbol variableSymbol) {
    switch (variableSymbol.getBlockType()) {
      case STATE:
      case EQUATIONS:
      case INITIAL_VALUES:
        return  "S_.";
      case PARAMETERS:
        return  "P_.";
      case INTERNALS:
        return  "V_.";
      case INPUT:
        return "B_.";
      default:
        return "";
    }

  }
}
