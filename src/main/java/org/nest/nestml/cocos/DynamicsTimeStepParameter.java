/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTDynamics;
import org.nest.nestml._ast.ASTParameter;
import org.nest.nestml._cocos.NESTMLASTDynamicsCoCo;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * The only parameter of the timestep dynamics must be of the type ms
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class DynamicsTimeStepParameter implements NESTMLASTDynamicsCoCo {
  public static final String ERROR_CODE = "NESTML_DYNAMICS_TIME_STEP_PARAMETER";

  public void check(final ASTDynamics dyn) {
    checkArgument(dyn.getEnclosingScope().isPresent(), "No scope assigned. Please run SymbolTableCreator");
    final Scope scope = dyn.getEnclosingScope().get();

    if (dyn.getTimeStep().isPresent()) {
      if (dyn.getParameters().isPresent()) {

        if (dyn.getParameters().get().getParameters().size() != 1) {
          final String msg = "Timestep-dynamics need exactly 1 parameter of type ms.";
          Log.error(ERROR_CODE + ":" + msg, dyn.get_SourcePositionStart());

        } else { // 1 parameters
          // start time: ms or ms
          final ASTParameter first = dyn.getParameters().get().getParameters().get(0);

          final String typeName = Names.getQualifiedName(first.getType().getParts());
          final Optional<TypeSymbol> type = scope.resolve(typeName, TypeSymbol.KIND);

          Preconditions.checkState(type.isPresent(), "Cannot find the type: " + typeName);
          // TODO fix the implicit type. its fqn contains the artifact fqn prefix
          if (!type.get().getName().endsWith("ms")) {
            final String msg = "The timestep-dynamics parameter needs to be of type <ms>";
           error(ERROR_CODE + ":" +  msg, first.get_SourcePositionStart());

          }


        }

      }
      else {
        final String msg = "Timestep-dynamics need exactly 1 parameter of type ms.";
       error(ERROR_CODE + ":" +  msg, dyn.get_SourcePositionStart());
      }

    }

  }

}
