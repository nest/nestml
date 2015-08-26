package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTDynamics;
import org.nest.nestml._ast.ASTParameter;
import org.nest.nestml._cocos.NESTMLASTDynamicsCoCo;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

public class DynamicsTimeStepParameter implements NESTMLASTDynamicsCoCo {
  public static final String ERROR_CODE = "NESTML_DYNAMICS_TIME_STEP_PARAMETER";

  public void check(ASTDynamics dyn) {
    checkArgument(dyn.getEnclosingScope().isPresent(), "No scope assigned. Please run SymbolTableCreator");
    final Scope scope = dyn.getEnclosingScope().get();

    if (dyn.getTimeStep().isPresent()) {
      if (dyn.getParameters().isPresent()
              && dyn.getParameters().get().getParameters() != null) {

        if (dyn.getParameters().get().getParameters().size() != 1) {
          final String msg = "Timestep-dynamics need exactly 1 parameter of type <fillme>.";
          CoCoLog.error(
              ERROR_CODE,
              msg,
              dyn.get_SourcePositionStart());

        } else { // 1 parameters
          // start time: ms or ms
          final ASTParameter first = dyn.getParameters().get().getParameters().get(0);

          final String typeName = Names.getQualifiedName(first.getType().getParts());
          final Optional<NESTMLTypeSymbol> type = scope.resolve(typeName, NESTMLTypeSymbol.KIND);

          Preconditions.checkState(type.isPresent(), "Cannot find the type: " + typeName);
          // TODO fix the implicit type. its fqn contains the artifact fqn prefix
          if (!type.get().getName().endsWith("ms")) {
            final String msg = "The timestep-dynamics parameter needs to be of type <ms>";
            CoCoLog.error(ERROR_CODE, msg, first.get_SourcePositionStart());

          }


        }

      }
      else {
        final String msg = "Timestep-dynamics need exactly 1 parameter of type <fillme>.";
        CoCoLog.error(ERROR_CODE, msg, dyn.get_SourcePositionStart());
      }

    }

  }

}
