package org.nest.spl.prettyprinter;

/**
 * Instantiates SPL printers. Optionally, set the indentation level which is useful for the
 * composition of printers.
 *
 * @author plotnikov
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
