package org.nest.codegeneration.helpers;

import de.monticore.literals.literals._ast.ASTSignedNumericLiteral;
import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import org.nest.spl._ast.ASTFOR_Stmt;

import java.math.BigDecimal;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * TODO
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 * @since TODO
 */
@SuppressWarnings({"unused"}) // the class is used from templates
public class SPLForNodes {

  private static final String LOG_NAME = SPLForNodes.class.getName();

  public String printComparisonOperator(final ASTFOR_Stmt ast) {
    Optional<ASTSignedNumericLiteral> step = ast.getStep();
    if (!step.isPresent()) {
      return  "<";
    }
    else {
      final String stepAsString = createPrettyPrinterForTypes().prettyprint(step.get());
      final BigDecimal stepV = new BigDecimal(stepAsString);
      if (stepV.compareTo(BigDecimal.ZERO) < 0) {
        return  ">";
      }
      else if (stepV.compareTo(BigDecimal.ZERO) > 0) {
        return  "<";
      }
      else {
        checkState(false, "The stepsize cannot be 0");
      }
    }

    throw new RuntimeException("Cannot determine which comparison operator to use");
  }

  public String printStep(final ASTFOR_Stmt ast) {
    Optional<ASTSignedNumericLiteral> step = ast.getStep();
    if (!step.isPresent()) {
      return  "1";
    }
    else {
      return createPrettyPrinterForTypes().prettyprint(step.get());
    }

  }

  private TypesPrettyPrinterConcreteVisitor createPrettyPrinterForTypes() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }
}
