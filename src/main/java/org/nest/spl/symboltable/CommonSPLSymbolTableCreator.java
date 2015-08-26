/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import de.monticore.symboltable.CommonSymbolTableCreator;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

/**
 * TODO why must I write this class?.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class CommonSPLSymbolTableCreator extends CommonSymbolTableCreator implements SPLSymbolTableCreator {

  private final PredefinedTypesFactory predefinedTypesFactory;

  public CommonSPLSymbolTableCreator(
      final ResolverConfiguration resolverConfig,
      final MutableScope enclosingScope,
      final PredefinedTypesFactory predefinedTypesFactory) {
    super(resolverConfig, enclosingScope);
    this.predefinedTypesFactory = predefinedTypesFactory;
  }

  @Override
  public PredefinedTypesFactory getTypesFactory() {
    return predefinedTypesFactory;
  }

}
