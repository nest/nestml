package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

public class NESTGetterSetterFunctionNames implements NESTMLASTFunctionCoCo {


  public static final String ERROR_CODE = "NESTML_GETTER_SETTER_FUNCTION_NAMES";

  public void check(final ASTFunction fun) {
    String funName = fun.getName();

    final Optional<? extends Scope> enclosingScope = fun.getEnclosingScope();
    Preconditions.checkState(enclosingScope.isPresent(), "There is no scope assigned to the AST node: " + fun.getName());

    NESTMLMethodSymbol me = getMethodEntry(fun, enclosingScope.get());

    if (me.getDeclaringNeuron().getType() == NESTMLNeuronSymbol.Type.COMPONENT
            && funName.equals("get_instance")
            && me.getParameterTypes().size() == 0) {

      final String msg = "The function '"
              + funName
              + "' is going to be generated. Please use another name.";
     error(ERROR_CODE + ":" +  msg, fun.get_SourcePositionStart());
      return;
    }

    if (funName.startsWith("get_") || funName.startsWith("set_")) {
      String varName = funName.substring(4);

      Optional<NESTMLVariableSymbol> var = enclosingScope.get().resolve(varName, NESTMLVariableSymbol.KIND) ;

      if (var.isPresent()) {

        if (funName.startsWith("set_")
                && me.getParameterTypes().size() == 1
                && !var.get().isAlias()) {
          final String msg = "The function '" + funName
                  + "' is going to be generated, since"
                  + " there is a variable called '" + varName
                  + "'.";
         error(ERROR_CODE + ":" +  msg, fun.get_SourcePositionStart());
        }

        if (funName.startsWith("get_")
                && me.getParameterTypes().size() == 0) {
          final String msg = "The function '" + funName
                  + "' is going to be generated, since"
                  + " there is a variable called '" + varName
                  + "'.";
         error(ERROR_CODE + ":" +  msg, fun.get_SourcePositionStart());
        }

      }

    }

  }

  private NESTMLMethodSymbol getMethodEntry(final ASTFunction fun, final Scope scope) {
    Optional<NESTMLMethodSymbol> me;

    if (!fun.getParameters().isPresent()) {
      me = NESTMLSymbols.resolveMethod(scope, fun.getName(), Lists.newArrayList());
    }
    else {
      List<String> parameters = Lists.newArrayList();
      for (int i = 0; i < fun.getParameters().get().getParameters().size(); ++i) {
        String parameterTypeFqn = Names.getQualifiedName(fun.getParameters().get().getParameters().get(i).getType().getParts());
        parameters.add(parameterTypeFqn);
      }

      me = NESTMLSymbols.resolveMethod(scope, fun.getName(), parameters);
    }

    Preconditions.checkState(me.isPresent(), "Cannot resolve the method: " + fun.getName());
    return me.get();
  }

}
