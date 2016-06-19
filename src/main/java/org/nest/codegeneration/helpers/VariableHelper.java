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
        return  "S_.";
      case PARAMETER:
        return  "P_.";
      case INTERNAL:
        return  "V_.";
      default:
        return "";
    }

  }
}
