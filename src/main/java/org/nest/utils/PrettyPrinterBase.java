package org.nest.utils;

/**
 * Created by user on 31.05.15.
 */
public class PrettyPrinterBase {
  protected static final String BLOCK_CLOSE = "end";

  protected static final String BLOCK_OPEN = ":";

  private String result = "";

  private int indentionLevel = 0;

  private String indent = "";

  public void setIndentionLevel(int indentionLevel) {
    this.indentionLevel = indentionLevel;
  }

  protected int getIndentionLevel() {
    return indentionLevel;
  }

  public void print(String s) {
    result += (indent + s);
    indent = "";
    calcIndention();
  }

  public void println() {
    println("");
  }

  public void println(String s) {
    result += (indent + s + "\n");
    indent = "";
    calcIndention();
  }

  private void calcIndention() {
    indent = "";
    for (int i = 0; i < indentionLevel; i++) {
      indent += "  ";
    }
  }

  protected void indent() {
    indentionLevel++;
    calcIndention();
  }

  protected void unindent() {
    indentionLevel--;
    calcIndention();
  }

  public String getResult() {
    return result;
  }
}
