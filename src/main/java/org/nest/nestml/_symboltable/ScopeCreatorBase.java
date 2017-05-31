/*
 * ScopeCreatorBase.java
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
package org.nest.nestml._symboltable;

import de.monticore.symboltable.GlobalScope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.predefined.PredefinedVariables;

/**
 * TODO
 *
 * @author plotnikov
 */
public abstract class ScopeCreatorBase {
  private final static String LOG_NAME = ScopeCreatorBase.class.getName();

  public void addPredefinedTypes(final GlobalScope globalScope) {
    PredefinedTypes.getTypes().forEach(
        type -> {
          globalScope.add(type);
          final String typeLogMsg = "Adds new implicit type declaration: %s";
          Log.trace(String.format(typeLogMsg, type.getName()), LOG_NAME);
        }
    );
  }

  public void addPredefinedFunctions(final GlobalScope globalScope) {

    PredefinedFunctions.getMethodSymbols().forEach(
        method -> {
          globalScope.add(method);
          final String methodLogMsg = String
              .format("Adds new implicit method declaration: %s", method.getName());
          Log.trace(methodLogMsg, LOG_NAME);
        }
    );
  }

  public void addPredefinedVariables(final GlobalScope globalScope) {

    PredefinedVariables.gerVariables().forEach(
        variable -> {
          globalScope.add(variable);
          final String methodLogMsg = String
              .format("Adds new implicit variable declaration: %s", variable.getName());
          Log.trace(methodLogMsg, LOG_NAME);
        }
    );

  }

}
