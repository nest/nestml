package org.nest.nestml.prettyprinter;

import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;

/**
 * Created by user on 09.06.15.
 */
public class NESTMLPrettyPrinterFactory {
  public static NESTMLPrettyPrinter createNESTMLPrettyPrinter() {
    return new NESTMLPrettyPrinter(new ExpressionsPrettyPrinter());
  }

}
