package org.nest.codegeneration.helpers;

import de.monticore.literals.literals._ast.ASTSignedNumericLiteral;
import de.monticore.prettyprint.IndentPrinter;
import de.monticore.types.prettyprint.TypesPrettyPrinterConcreteVisitor;
import org.nest.nestml._ast.ASTFOR_Stmt;

import java.math.BigDecimal;

import static com.google.common.base.Preconditions.checkState;

/**
 * Provides helper methods to print information from the for-loop AST.
 *
 * @author plotnikov
 */
@SuppressWarnings({"unused"}) // the class is used from templates
public class ASTForNodes {

  private static final String LOG_NAME = ASTForNodes.class.getName();

  public String printComparisonOperator(final ASTFOR_Stmt ast) {
    ASTSignedNumericLiteral step = ast.getStep();
    final String stepAsString = createPrettyPrinterForTypes().prettyprint(step);
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


    throw new RuntimeException("Cannot determine which comparison operator to use");
  }

  public String printStep(final ASTFOR_Stmt ast) {
    ASTSignedNumericLiteral step = ast.getStep();
    return createPrettyPrinterForTypes().prettyprint(step);
  }

  private TypesPrettyPrinterConcreteVisitor createPrettyPrinterForTypes() {
    final IndentPrinter printer = new IndentPrinter();
    return new TypesPrettyPrinterConcreteVisitor(printer);
  }
}
