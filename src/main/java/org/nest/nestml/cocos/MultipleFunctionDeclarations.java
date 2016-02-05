/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.resolving.ResolvedSeveralEntriesException;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTParameter;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;
import org.nest.symboltable.symbols.NeuronSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Methods must be unique. If there are two methods with same name, than they must have
 * different argument types.
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class MultipleFunctionDeclarations implements NESTMLASTNeuronCoCo, NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_MULTIPLE_FUNCTIONS_DECLARATIONS";


  @Override
  public void check(final ASTComponent astComponent) {
    final ASTBody astBodyDecorator = astComponent.getBody();
    final Optional<NeuronSymbol> componentSymbol
        = (Optional<NeuronSymbol>) astComponent.getSymbol();
    checkState(componentSymbol.isPresent());
    astBodyDecorator.getFunctions().forEach(astFunction -> checkFunctionName(astFunction,
        componentSymbol.get()));
  }


  @Override public void check(final ASTNeuron astNeuron) {
    final ASTBody astBodyDecorator = (astNeuron.getBody());
    final Optional<NeuronSymbol> neuronSymbol
        = (Optional<NeuronSymbol>) astNeuron.getSymbol();
    checkState(neuronSymbol.isPresent());
    astBodyDecorator.getFunctions().forEach(astFunction -> checkFunctionName(astFunction, neuronSymbol.get()));
  }

  private void checkFunctionName(
      final ASTFunction astFunction,
      final NeuronSymbol neuronSymbol) {

    String funname = astFunction.getName();

    final ASTParameter[] params;
    if (astFunction.getParameters().isPresent()
        && astFunction.getParameters().get().getParameters().size() > 0) {
      params = astFunction.getParameters().get().getParameters().toArray(new ASTParameter[0]);
    } else {
      params = new ASTParameter[0];
    }


    try {
      // throws a ResolvedSeveralEntriesException exception in case the name is unambiguous
      neuronSymbol.getMethodByName(funname);


    }
    catch (ResolvedSeveralEntriesException e) {
      final String msg = "The function '" + funname + "' with "
          + params.length
          + " parameter(s) is defined multiple times.";
      error(ERROR_CODE + ":" + msg, astFunction.get_SourcePositionStart());
    }
  }

}
