/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.helpers.GslNames;
import org.nest.codegeneration.helpers.Names;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.spl.prettyprinter.IReferenceConverter;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.SIData;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static com.google.common.base.Preconditions.checkState;
import static java.lang.Math.pow;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;
import static org.nest.utils.AstUtils.convertDevrivativeNameToSimpleName;
import static org.nest.utils.AstUtils.convertSiName;

import java.util.Optional;

/**
 * Makes a conversion for the GSL solver.
 *
 * @author plotnikov
 */
public class GslReferenceConverter implements IReferenceConverter {

  private final boolean isUseUpperBound;
  private static final Double MAXIMAL_EXPONENT = 10.0;

  public GslReferenceConverter() {
    isUseUpperBound = false; // TODO make it parametrizable
  }

  @Override
  public String convertBinaryOperator(String binaryOperator) {
    if (binaryOperator.equals("**")) {
      return "pow(%s, %s)";
    }
    else {
      return "(%s)" + binaryOperator + "(%s)";
    }
  }

  @Override
  public String convertFunctionCall(final ASTFunctionCall astFunctionCall) {
    final String functionName = astFunctionCall.getCalleeName();

    // Time.resolution() -> nestml::Time::get_resolution().get_ms
    if ("resolution".equals(functionName)) {
      return "nest::Time::get_resolution().get_ms()";
    }
    // Time.steps -> nest::Time(nest::Time::ms( args )).get_steps());
    if ("steps".equals(functionName)) {
      return "nest::Time(nest::Time::ms((double) %s)).get_steps()";
    }

    if (PredefinedFunctions.POW.equals(functionName)) {
      return "std::pow(%s)";
    }

    if (PredefinedFunctions.LOG.equals(functionName)) {
      return "std::log(%s)";
    }

    if ("expm1".equals(functionName)) {
      return "numerics::expm1(%s)";
    }

    if ("exp".equals(functionName)) {

      if (isUseUpperBound) {
        return "std::exp(std::min(%s, " + MAXIMAL_EXPONENT + "))";
      }
      else {
        return "std::exp(%s)";

      }

    }
    if (PredefinedFunctions.POW.equals(functionName)) {
      return "pow(%s)";
    }
    if (PredefinedFunctions.MAX.equals(functionName) || PredefinedFunctions.BOUNDED_MAX.equals(functionName)) {
      return "std::max(%s)";
    }
    if (PredefinedFunctions.MIN.equals(functionName)|| PredefinedFunctions.BOUNDED_MIN.equals(functionName)) {
      return "std::min(%s)";
    }
    if (functionName.contains(PredefinedFunctions.EMIT_SPIKE)) {
      return "set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n" +
             "nest::SpikeEvent se;\n" +
             "nest::kernel().event_delivery_manager.send(*this, se, lag);";
    }

    throw new UnsupportedOperationException("Cannot map the function: '" + functionName +"'");
  }

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkState(astVariable.getEnclosingScope().isPresent(), "Run symbol table creator.");
    final String variableName = convertDevrivativeNameToSimpleName(astVariable);
    final Scope scope = astVariable.getEnclosingScope().get();
    final VariableSymbol variableSymbol = VariableSymbol.resolve(astVariable.toString(), scope);

    Optional<String> siUnitAsLiteral = convertSiName(astVariable.toString());
    if(siUnitAsLiteral.isPresent()){
      return siUnitAsLiteral.get();
    }

    if (variableSymbol.definedByODE()) {
      return GslNames.name(variableSymbol);
    }
    else if (variableSymbol.isBuffer()) {
      return "node.B_." + Names.bufferValue(variableSymbol);
    }
    else {

      if (PredefinedVariables.E_CONSTANT.equals(variableName)) {
        return "numerics::e";
      }
      else {
        if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL) || variableSymbol.isAlias()) {
          return variableName;
        }
        else {
          if (variableSymbol.getVectorParameter().isPresent()) {
            return "node.get_" + variableName + "()[i]";
          }
          else {
            return "node.get_" + variableName + "()";
          }

        }

      }

    }

  }



  @Override
  public String convertConstant(final String constantName) {
    return constantName;
  }

}
