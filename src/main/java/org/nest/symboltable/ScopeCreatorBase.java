/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import de.monticore.symboltable.GlobalScope;
import de.se_rwth.commons.logging.Log;
import org.nest.symboltable.predefined.PredefinedFunctionFactory;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.predefined.PredefinedVariablesFactory;

/**
 * TODO
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since TODO
 */
public abstract class ScopeCreatorBase {

  protected final PredefinedTypesFactory typesFactory;
  protected final PredefinedFunctionFactory functionFactory;
  protected final PredefinedVariablesFactory variablesFactory;

  public abstract String getLogger();

  public ScopeCreatorBase(final PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
    this.functionFactory = new PredefinedFunctionFactory(typesFactory);
    this.variablesFactory = new PredefinedVariablesFactory(typesFactory);
  }

  public PredefinedTypesFactory getTypesFactory() {
    return typesFactory;
  }

  public void addPredefinedTypes(final GlobalScope globalScope) {
    typesFactory.getTypes().forEach(
        type -> {
          globalScope.define(type);
          final String typeLogMsg = "Adds new implicit type declaration: %s";
          Log.info(String.format(typeLogMsg, type.getName()), getLogger());
        }
    );
  }

  public void addPredefinedFunctions(final GlobalScope globalScope) {

    functionFactory.getMethodSymbols().forEach(
        method -> {
          globalScope.define(method);
          final String methodLogMsg = String
              .format("Adds new implicit method declaration: %s", method.getName());
          Log.info(methodLogMsg, getLogger());
        }
    );
  }

  public void addPredefinedVariables(final GlobalScope globalScope) {

    variablesFactory.gerVariables().forEach(
        variable -> {
          globalScope.define(variable);
          final String methodLogMsg = String
              .format("Adds new implicit variable declaration: %s", variable.getName());
          Log.info(methodLogMsg, getLogger());
        }
    );

  }

}
