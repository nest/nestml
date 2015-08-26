/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTDynamics;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Prints the dynamics function.
 *
 * @author plotnikov
 * @since 0.0.1
 */
@SuppressWarnings("unused")
public class NESTMLDynamicsPrinter {

  public static final String DEFAULT_DYNAMICS_NAME = "dynamics";

  public final PredefinedTypesFactory typesFactory;

  public NESTMLDynamicsPrinter(PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
  }

  public String printDynamicsType(final ASTDynamics dynamics) {
    checkArgument(dynamics.getEnclosingScope().isPresent());
    final Scope scope = dynamics.getEnclosingScope().get();

    List<String> parameters = Lists.newArrayList();
    for (int i = 0; i < dynamics.getParameters().get().getParameters().size(); ++i) {
      String parameterTypeFqn = Names.getQualifiedName(dynamics.getParameters().get().getParameters().get(i).getType().getParts());
      parameters.add(parameterTypeFqn);
    }

    Optional<NESTMLMethodSymbol> dynamicsSymbol = NESTMLSymbols.resolveMethod(scope, DEFAULT_DYNAMICS_NAME, parameters);
    checkState(dynamicsSymbol.isPresent(), "Cannot resolve neuron's dynamic: " + DEFAULT_DYNAMICS_NAME);

    String typeName = new NESTML2NESTTypeConverter(typesFactory).convert(dynamicsSymbol.get().getParameterTypes().get(0));
    return typeName.replace(".", "::");
  }

  public String printParameterName(final ASTDynamics dynamics) {
    checkArgument(dynamics.getEnclosingScope().isPresent());
    final Scope scope = dynamics.getEnclosingScope().get();

    List<String> parameterNames = Lists.newArrayList();
    for (int i = 0; i < dynamics.getParameters().get().getParameters().size(); ++i) {
      parameterNames.add(dynamics.getParameters().get().getParameters().get(i).getName());
    }

    return parameterNames.get(0);
  }

}
