/*
 * SPLPrettyPrinterFactory.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.nest.nestml.prettyprinter;

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
