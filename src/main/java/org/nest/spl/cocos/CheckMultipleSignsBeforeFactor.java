/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.cocos;

import com.google.common.base.Joiner;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import de.monticore.ast.ASTCList;
import de.monticore.ast.ASTCNode;
import de.monticore.cocos.CoCoLog;
import org.nest.spl._ast.ASTBlock;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._cocos.SPLASTBlockCoCo;
import org.nest.spl._cocos.SPLASTExprCoCo;
import org.nest.utils.ASTNodes;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Forbids expressions like: ---a
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class CheckMultipleSignsBeforeFactor implements SPLASTExprCoCo, SPLASTBlockCoCo {

  public static final String ERROR_CODE = "MULTIPLE_SIGNS_BEFORE_FACTOR";

  private static final String ERROR_MSG_FORMAT =
      "Factor has too many signs in front of it:  %s.";

  private Optional<ASTCNode> root = Optional.empty();

  @Override
  public void check(ASTBlock node) {
    //root = Optional.of(node);
  }

  // TODO reactivate this condition later
  public void check(ASTExpr factor) {
    //checkState(root.isPresent());
    /*Optional<ASTNode> parentOfFactor = ASTNodes.getParent(factor, root.get());
    checkState(parentOfFactor.isPresent());


    if (!(parentOfFactor.get() instanceof ASTExpr) &&
        !(parentOfFactor.get() instanceof ASTCList)) { // top-level factor
      List<Sign> signs = Lists.newArrayList();
      int plus = 0, minus = 0, tilde = 0;
      getSigns(factor, signs);
      for (Sign sign : signs) {
        switch (sign) {
          case PLUS:
            ++plus;
            break;
          case MINUS:
            ++minus;
            break;
          case TILDE:
            ++tilde;
            break;
          default:
            break;
        }
      }
      if (plus > 1 || minus > 1 || tilde > 1 || (plus > 0 && minus > 0)) {
        CoCoLog.error(ERROR_CODE,
            String.format(ERROR_MSG_FORMAT, Joiner.on("").join(signs)),  // TODO must be possible to compute information about signs
            factor.get_SourcePositionStart());
      }
    }*/

  }

  /**
   * Recursively insert signes into the list s.
   */
  private List<Sign> getSigns(ASTExpr f, List<Sign> s) {
    if (f.getTerm().isPresent()) {
      if (f.isUnaryPlus()) {
        s.add(Sign.PLUS);
      }
      if (f.isUnaryMinus()) {
        s.add(Sign.MINUS);
      }
      if (f.isUnaryTilde()) {
        s.add(Sign.TILDE);
      }

      return getSigns(f.getTerm().get(), s);
    }
    else {
      return s;
    }

  }

  enum Sign {
    PLUS("+"), MINUS("-"), TILDE("~");

    public final String sign;

    Sign(String s) {
      this.sign = s;
    }

    public String toString() {
      return this.sign;
    }
  }

}
