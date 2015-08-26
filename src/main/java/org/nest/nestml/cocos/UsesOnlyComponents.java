package org.nest.nestml.cocos;


import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTUSE_Stmt;
import org.nest.nestml._cocos.NESTMLASTUSE_StmtCoCo;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

public class UsesOnlyComponents implements NESTMLASTUSE_StmtCoCo {

  public final static String ERROR_CODE = "NESTML_USES_ONLY_COMPONENTS";


  public void check(ASTUSE_Stmt use) {
    checkArgument(use.getEnclosingScope().isPresent(), "No scope was assigned. Please, run symboltable creator.");
    final String typeName = Names.getQualifiedName(use.getName().getParts());

    final Scope scope = use.getEnclosingScope().get();

    final Optional<NESTMLTypeSymbol> predefinedType = scope.resolve(typeName, NESTMLTypeSymbol.KIND);

    if (predefinedType.isPresent()) {
      final String msg = "Only components can be used by neurons/components and not " + typeName + " of the type: " +
          predefinedType.get().getType() + " .";
      CoCoLog.error(ERROR_CODE, msg);
    }

    final Optional<NESTMLNeuronSymbol> neuronType = scope.resolve(typeName, NESTMLNeuronSymbol.KIND);

    if (neuronType.isPresent() && !neuronType.get().getType().equals(NESTMLNeuronSymbol.Type.COMPONENT)) {
      final String msg = "Only components can be used by components and not " + typeName + " that is a neuron, not a "
          + "component";

      CoCoLog.error(ERROR_CODE, msg);
    }
    // Undefined type of the name
  }

}
