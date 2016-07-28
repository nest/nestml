package org.nest.codegeneration.sympy;

import com.google.common.base.Preconditions;
import de.monticore.ast.ASTNode;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.ode._ast.ASTEquation;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.utils.ASTUtils;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;


/**
 * Provides methods to manipulate ODEs: replace all I_sum(shape, buffer) and Cond_sum(shape, buffer) through the
 * corresponding shape. This class is used also in generator templates
 *
 * @author plotnikov
 */
public class ODETransformer {
  // this function is used in freemarker templates und must be public
  public static ASTEquation replaceSumCalls(final ASTEquation astOde) {
    final ASTEquation workingCopy = astOde.deepClone();
    final List<ASTFunctionCall> functions = getSumFunctionCalls(workingCopy);

    functions.forEach(node -> replaceFunctionCallThroughFirstArgument(workingCopy, node));
    return workingCopy;
  }

  public static List<ASTFunctionCall> getSumFunctionCalls(ASTEquation workingCopy) {
    return ASTUtils.getAll(workingCopy, ASTFunctionCall.class)
          .stream()
          .filter(astFunctionCall ->
              astFunctionCall.getCalleeName().equals(PredefinedFunctions.I_SUM) ||
              astFunctionCall.getCalleeName().equals(PredefinedFunctions.COND_SUM))
          .collect(Collectors.toList());
  }

  public static List<ASTFunctionCall> getCondSumFunctionCall(ASTEquation workingCopy) {
    return ASTUtils.getAll(workingCopy, ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(PredefinedFunctions.COND_SUM))
        .collect(Collectors.toList());
  }

  private static void replaceFunctionCallThroughFirstArgument(ASTEquation astOde, ASTFunctionCall node) {
    final Optional<ASTNode> parent = ASTUtils.getParent(node, astOde);
    Preconditions.checkState(parent.isPresent());
    final ASTExpr expr = (ASTExpr) parent.get();
    expr.setFunctionCall(null);
    expr.setVariable(node.getArgs().get(0).getVariable().get());
  }
}