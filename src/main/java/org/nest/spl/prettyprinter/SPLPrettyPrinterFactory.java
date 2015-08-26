package org.nest.spl.prettyprinter;

/**
 * Created by user on 09.06.15.
 */
public class SPLPrettyPrinterFactory {
  public static SPLPrettyPrinter createDefaultPrettyPrinter() {
    return new SPLPrettyPrinter(new ExpressionsPrettyPrinter());

  }

  public static SPLPrettyPrinter createDefaultPrettyPrinter(int indentionLevel) {
    final SPLPrettyPrinter splPrettyPrinter =
        new SPLPrettyPrinter(new ExpressionsPrettyPrinter());
    splPrettyPrinter.setIndentionLevel(indentionLevel);
    return splPrettyPrinter;

  }

}
