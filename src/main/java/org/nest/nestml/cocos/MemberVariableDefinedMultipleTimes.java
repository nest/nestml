package org.nest.nestml.cocos;


import com.google.common.collect.Maps;
import static de.se_rwth.commons.logging.Log.error;
import de.se_rwth.commons.SourcePosition;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;
import org.nest.nestml._cocos.NESTMLASTNeuronCoCo;
import org.nest.spl._ast.ASTDeclaration;

import java.util.Map;

/**
 * This context condition checks, whether the state/parameter/internal-variables
 * of a component/neuron is not defined multiple times.
 *
 * E.g. in the following case x defined twice and results in an error
 * neuron NeuronInTest:
 *   state: x mV end
 *   parameter: x real end
 * end
 *
 * @author Tammo Ippen
 */
public class MemberVariableDefinedMultipleTimes implements NESTMLASTNeuronCoCo,
    NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_MEMBER_VARIABLE_DEFINED_MULTIPLE_TIMES";

  public void check(ASTComponent comp) {
    check(comp.getBody());
  }

  public void check(ASTNeuron neuron) {
    check(neuron.getBody());
  }

  private void check(ASTBody body) {
    ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(body);
    Map<String, SourcePosition> varNames = Maps.newHashMap();
    bodyDecorator.getStates().forEach(aliasDecl -> addNames(varNames, aliasDecl.getDeclaration()));
    bodyDecorator.getParameters().forEach(aliasDecl -> addNames(varNames, aliasDecl.getDeclaration()));
    bodyDecorator.getInternals().forEach(aliasDecl -> addNames(varNames, aliasDecl.getDeclaration()));
  }

  private void addNames(Map<String, SourcePosition> names, ASTDeclaration decl) {
    for (String var : decl.getVars()) {
      if (names.containsKey(var)) {
        final String msg = "Variable '" + var + "' defined previously defined i line: "
                + names.get(var).getLine() + ":" + names.get(var).getColumn();

       error(ERROR_CODE + ":" +  msg, decl.get_SourcePositionStart());

      }
      else {
        names.put(var, decl.get_SourcePositionStart());
      }

    }

  }

}
