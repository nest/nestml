package org.nest.codegeneration.helpers;

import org.nest.symboltable.symbols.VariableSymbol;

/**
 * Provides helper methods for the printing variables for the nest taget
 * @author plotnikov
 */
public class VariableHelper {
  static public String printOrigin(final VariableSymbol variableSymbol) {
    switch (variableSymbol.getBlockType()) {
      case STATE:
      case EQUATION:
        return  "S_.";
      case PARAMETER:
        return  "P_.";
      case INTERNAL:
        return  "V_.";
      case INPUT_BUFFER_CURRENT: case INPUT_BUFFER_SPIKE:
        return "B_.";
      default:
        return "";
    }

  }
}
