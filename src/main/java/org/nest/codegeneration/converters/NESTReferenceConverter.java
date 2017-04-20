/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.spl.prettyprinter.IReferenceConverter;
import org.nest.symboltable.NestmlSymbols;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.predefined.PredefinedVariables;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units.unitrepresentation.SIData;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static java.lang.Math.pow;
import static org.nest.codegeneration.helpers.VariableHelper.printOrigin;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;
import static org.nest.symboltable.symbols.VariableSymbol.resolve;
import static org.nest.utils.AstUtils.convertSiName;

/**
 * Converts constants, names and functions the NEST equivalents.
 *
 * @author plotnikov
 */
public class NESTReferenceConverter implements IReferenceConverter {

  @Override
  public String convertBinaryOperator(final String binaryOperator) {
    if (binaryOperator.equals("**")) {
      return "pow(%s, %s)";
    }
    if (binaryOperator.equals("and")) {
      return "(%s) && (%s)";
    }
    if (binaryOperator.equals("or")) {
      return "(%s) || (%s)";
    }

    return "(%s)" + binaryOperator + "(%s)";
  }

  @Override
  public String convertFunctionCall(final ASTFunctionCall astFunctionCall) {
    checkState(astFunctionCall.getEnclosingScope().isPresent(), "No scope assigned. Run SymbolTable creator.");

    final Scope scope = astFunctionCall.getEnclosingScope().get();
    final String functionName = astFunctionCall.getCalleeName();

    if ("and".equals(functionName)) {
      return "&&";
    }

    if ("or".equals(functionName)) {
      return "||";
    }
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
    if (PredefinedFunctions.MAX.equals(functionName) || PredefinedFunctions.BOUNDED_MAX.equals(functionName)) {
      return "std::max(%s)";
    }
    if (PredefinedFunctions.MIN.equals(functionName) || PredefinedFunctions.BOUNDED_MIN.equals(functionName) ) {
      return "std::min(%s)";
    }

    if (PredefinedFunctions.EXP.equals(functionName)) {
      return "std::exp(%s)";
    }

    if (PredefinedFunctions.LOG.equals(functionName)) {
      return "std::log(%s)";
    }

    if ("expm1".equals(functionName)) {
      return "numerics::expm1(%s)";
    }

    if (functionName.contains(PredefinedFunctions.EMIT_SPIKE)) {
      return "set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n" +
          "nest::SpikeEvent se;\n" +
          "nest::kernel().event_delivery_manager.send(*this, se, lag);";
    }

    final Optional<MethodSymbol> functionSymbol = NestmlSymbols.resolveMethod(astFunctionCall);

    if (needsArguments(astFunctionCall)) {
      return functionName + "(%s)";
    }
    else {
      return functionName + "()";
    }

  }

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    checkArgument(astVariable.getEnclosingScope().isPresent(), "Run symboltable creator");
    final String variableName = AstUtils.convertDevrivativeNameToSimpleName(astVariable);
    final Scope scope = astVariable.getEnclosingScope().get();

    Optional<String> siUnitAsLiteral = convertSiName(astVariable.toString());
    if(siUnitAsLiteral.isPresent()){
      return siUnitAsLiteral.get();
    }

    if (PredefinedVariables.E_CONSTANT.equals(variableName)) {
      return "numerics::e";
    }
    else {
      final VariableSymbol variableSymbol = resolve(variableName, scope);
      if (variableSymbol.getBlockType().equals(VariableSymbol.BlockType.LOCAL)) {
        return variableName + (variableSymbol.isVector()?"[i]":"");
      }
      else if(variableSymbol.isBuffer()) {
        return printOrigin(variableSymbol) + org.nest.codegeneration.helpers.Names.bufferValue(variableSymbol) + (variableSymbol.isVector()?"[i]":"");
      }
      else {
        if (variableSymbol.isAlias()) {
          return "get_" + variableName + "()" +  (variableSymbol.isVector()?"[i]":"") ;
        }
        else {

          return printOrigin(variableSymbol) + variableName +  (variableSymbol.isVector()?"[i]":"");
        }

      }

    }

  }

  @Override
  public String convertConstant(final String constantName) {
    if ("inf".equals(constantName)) {
      return "std::numeric_limits<double_t>::infinity()";
    }
    else {
      return constantName;
    }

  }

}
