package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.monticore.utils.ASTNodes.getSuccessors;

// TODO write a corresponding test
public class AliasInNonAliasDecl implements NESTMLASTNeuronCoCo, NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_ALIAS_IN_NON_ALIAS_DECL";

  @Override
  public void check(ASTComponent astComponent) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(astComponent.getBody());
    final Optional<NESTMLNeuronSymbol> componentSymbol
        = (Optional<NESTMLNeuronSymbol>) astComponent.getSymbol();
    checkState(componentSymbol.isPresent());
    checkAllAliasesInNeuron(astBodyDecorator, componentSymbol.get());
  }


  @Override
  public void check(ASTNeuron astNeuron) {
    final ASTBodyDecorator astBodyDecorator = new ASTBodyDecorator(astNeuron.getBody());
    final Optional<NESTMLNeuronSymbol> neuronSymbol
        = (Optional<NESTMLNeuronSymbol>) astNeuron.getSymbol();
    checkState(neuronSymbol.isPresent());
    checkAllAliasesInNeuron(astBodyDecorator, neuronSymbol.get());
  }

  public void checkAllAliasesInNeuron(
      final ASTBodyDecorator astBodyDecorator,
      final NESTMLNeuronSymbol neuronSymbol) {
    astBodyDecorator.getInternals().forEach(astFunction -> checkAlias(astFunction,
        neuronSymbol));
    astBodyDecorator.getStates().forEach(astFunction -> checkAlias(astFunction,
        neuronSymbol));
    astBodyDecorator.getParameters().forEach(astFunction -> checkAlias(astFunction,
        neuronSymbol));
  }

  public void checkAlias(final ASTAliasDecl alias, final NESTMLNeuronSymbol neuronSymbol) {
    if (!alias.isAlias() && alias.getDeclaration().exprIsPresent()) {
      final ASTDeclaration decl = alias.getDeclaration();
      Optional<NESTMLVariableSymbol> used;

      final List<ASTQualifiedName> variables
          = getSuccessors(decl.getExpr().get(), ASTQualifiedName.class);
      // TODO Review the "reflection code"
      for (final ASTQualifiedName atomFqn : variables) {
        final String fullName = Names.getQualifiedName(atomFqn.getParts());

        final Optional<NESTMLVariableSymbol> stentry = neuronSymbol.getVariableByName(fullName);
        if (stentry.isPresent()) {
          used = stentry;
        }
        else {
          continue;
        }

        if (!used.isPresent()) { // should not happen, but makes compiler
          continue;
        }

        // used is set here
        if (used.get().isAlias()) {
          final String msg = "Alias variable '"
                  + used.get().getName()
                  + "' cannot be used in default-value declaration of non-alias variables.";
          error(ERROR_CODE + ":" + msg, decl.get_SourcePositionStart());
        }

      }

    }

  }

}
