/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTUSE_Stmt;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * For use statement only components ara allowed.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class UsesOnlyComponents implements NESTMLASTUSE_StmtCoCo {

  public final static String ERROR_CODE = "NESTML_USES_ONLY_COMPONENTS";
  CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();

  public void check(final ASTUSE_Stmt use) {
    checkArgument(use.getEnclosingScope().isPresent(), "No scope was assigned. Please, run symboltable creator.");
    final String typeName = Names.getQualifiedName(use.getName().getParts());

    final Scope scope = use.getEnclosingScope().get();

    final Optional<TypeSymbol> predefinedType = scope.resolve(typeName, TypeSymbol.KIND);

    if (predefinedType.isPresent()) {
      final String msg = errorStrings.getErrorMsgOnlyComponentsForNeurons(this,
              typeName,
              predefinedType.get().getType().toString());

      Log.error(msg, use.get_SourcePositionStart());
    }

    final Optional<NeuronSymbol> neuronType = scope.resolve(typeName, NeuronSymbol.KIND);

    if (neuronType.isPresent()) {
      if (!neuronType.get().getType().equals(NeuronSymbol.Type.COMPONENT)) {
        final String msg = errorStrings.getErrorMsgOnlyComponentsForComponents(this, typeName);
        Log.error(msg, use.get_SourcePositionStart());

      }

    }
    // Undefined type of the name
  }

}
