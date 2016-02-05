/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import de.monticore.symboltable.GlobalScope;
import de.se_rwth.commons.logging.Log;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.predefined.PredefinedVariables;

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
