/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

/**
 * Defines the base for NESTML related pretty printer.
 *
 * @author plotnikov
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
  }

  public void println() {
    print("\n");
    indent = "";
    calcIndention();
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

  public String result() {
    return result;
  }
}
