package org.nest.nestml._cocos;

import static com.google.common.base.Preconditions.checkArgument;
import java.util.Optional;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

/**
 * @author ptraeder
 */
public class LiteralsHaveTypes implements SPLASTAssignmentCoCo,SPLASTDeclarationCoCo {
  public static final String ERROR_CODE = "NESTML_LITERALS_MUST_HAVE_TYPES";

  @Override
  public void check(ASTAssignment node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
      checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
      Optional<VariableSymbol> var = enclosingScope.get().resolve(node.getLhsVarialbe().getName().toString(),VariableSymbol.KIND);
      if(var.isPresent()) {
        if (var.get().getType().getType() == TypeSymbol.Type.UNIT) {
          if (node.getExpr().nESTMLNumericLiteralIsPresent()) {
            if (!node.getExpr().getNESTMLNumericLiteral().get().getType().isPresent()) {

              CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
              final String msg = errorStrings.getErrorMsg(this);
              Log.error(msg, node.get_SourcePositionStart());
            }
          }
        }
      }

  }

  @Override
  public void check(ASTDeclaration node) {
    final Optional<? extends Scope> enclosingScope = node.getEnclosingScope();
    checkArgument(enclosingScope.isPresent(), "No scope was assigned. Please, run symboltable creator.");
    //resovle with the first var name from the declaration
    Optional<VariableSymbol> var = enclosingScope.get().resolve(node.getVars().get(0),VariableSymbol.KIND);
    if(var.isPresent()) {
      if (var.get().getType().getType() == TypeSymbol.Type.UNIT) {
        if (node.getExpr().isPresent()) {
          if(node.getExpr().get().getNESTMLNumericLiteral().isPresent())
          if (!node.getExpr().get().getNESTMLNumericLiteral().get().getType().isPresent()) {
            CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
            final String msg = errorStrings.getErrorMsg(this);
            Log.error(msg, node.get_SourcePositionStart());
          }
        }
      }
    }
  }
}
