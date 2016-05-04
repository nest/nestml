/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.collect.Maps;
import de.se_rwth.commons.Names;
import org.nest.symboltable.symbols.MethodSymbol;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static java.util.stream.Collectors.toList;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * Defines a set with implicit type functions, like {@code print, pow, ...}
 *
 * @author plotnikov
 */
public class PredefinedFunctions {

  private static final String TIME_RESOLUTION = "resolution";
  private static final String TIME_STEPS = "steps";
  private static final String EMIT_SPIKE = "emitSpike";
  private static final String PRINT = "print";
  private static final String PRINTLN = "println";
  private static final String POW = "pow";
  private static final String EXP = "exp";
  private static final String LOGGER_INFO = "info";
  private static final String LOGGER_WARNING = "warning";
  private static final String RANDOM = "random";
  private static final String RANDOM_INT = "randomInt";
  private static final String EXPM1 = "expm1";
  private static final String DELTA = "delta";
  private static final String MAX = "max";
  public static final String INTEGRATE = "integrate";
  public static final String I_SUM = "I_sum";


  private static final Map<String, MethodSymbol> name2FunctionSymbol = Maps.newHashMap();

  static {
    final MethodSymbol timeSteps = createFunctionSymbol(TIME_STEPS);
    timeSteps.addParameterType(getType("ms"));
    timeSteps.setReturnType(getIntegerType());
    name2FunctionSymbol.put(TIME_STEPS, timeSteps);

    final MethodSymbol emitSpike = createFunctionSymbol(EMIT_SPIKE);
    emitSpike.setReturnType(getRealType());
    name2FunctionSymbol.put(EMIT_SPIKE, emitSpike);

    // create
    final MethodSymbol printMethod = createFunctionSymbol(PRINT);
    printMethod.addParameterType(getStringType());
    printMethod.setReturnType(getVoidType());
    name2FunctionSymbol.put(PRINT, printMethod);

    final MethodSymbol printlnMethod = createFunctionSymbol(PRINTLN);
    printlnMethod.setReturnType(getVoidType());
    name2FunctionSymbol.put(PRINTLN, printlnMethod);

    final MethodSymbol powMethod = createFunctionSymbol(POW);
    powMethod.addParameterType(getRealType()); // base
    powMethod.addParameterType(getRealType()); // exp
    powMethod.setReturnType(getRealType());
    name2FunctionSymbol.put(POW, powMethod);

    final MethodSymbol expMethod = createFunctionSymbol(EXP);
    expMethod.addParameterType(getRealType()); // base
    expMethod.setReturnType(getRealType());
    name2FunctionSymbol.put(EXP, expMethod);

    final MethodSymbol loggerInfoMethod = createFunctionSymbol(LOGGER_INFO);
    loggerInfoMethod.addParameterType(getStringType());
    loggerInfoMethod.setReturnType(getVoidType());
    name2FunctionSymbol.put(LOGGER_INFO, loggerInfoMethod);

    final MethodSymbol loggerWarningMethod = createFunctionSymbol(LOGGER_WARNING);
    loggerWarningMethod.addParameterType(getStringType());
    loggerWarningMethod.setReturnType(getVoidType());
    name2FunctionSymbol.put(LOGGER_WARNING, loggerWarningMethod);

    final MethodSymbol randomMethod = createFunctionSymbol(RANDOM);
    randomMethod.setReturnType(getRealType());
    name2FunctionSymbol.put(RANDOM, randomMethod);

    final MethodSymbol randomIntMethod = createFunctionSymbol(RANDOM_INT);
    randomIntMethod.setReturnType(getIntegerType());
    name2FunctionSymbol.put(RANDOM_INT, randomIntMethod);

    final MethodSymbol timeResolution = createFunctionSymbol(TIME_RESOLUTION);
    timeResolution.setReturnType(getRealType());
    name2FunctionSymbol.put(TIME_RESOLUTION, timeResolution);

    final MethodSymbol expm1 = createFunctionSymbol(EXPM1);
    expm1.addParameterType(getRealType());
    expm1.setReturnType(getRealType());
    name2FunctionSymbol.put(EXPM1, expm1);

    final MethodSymbol delta = createFunctionSymbol(DELTA);
    delta.addParameterType(getType("ms"));
    delta.addParameterType(getType("ms"));
    delta.setReturnType(getType("real"));
    name2FunctionSymbol.put(DELTA, delta);

    final MethodSymbol max = createFunctionSymbol(MAX);
    max.addParameterType(getType("mV"));
    max.addParameterType(getType("mV"));
    max.setReturnType(getType("mV"));
    name2FunctionSymbol.put(MAX, max);

    final MethodSymbol integrate = createFunctionSymbol(INTEGRATE);
    integrate.addParameterType(getRealType());
    integrate.setReturnType(getVoidType());
    name2FunctionSymbol.put(INTEGRATE, integrate);

    final MethodSymbol i_sum = createFunctionSymbol(I_SUM);
    i_sum.addParameterType(getType("ms"));
    i_sum.addParameterType(getBufferType());
    i_sum.setReturnType(getType("pA"));
    name2FunctionSymbol.put(I_SUM, i_sum);
  }

  private static MethodSymbol createFunctionSymbol(final String functionName) {
    final String packageName = Names.getQualifier(functionName);
    final String simpleFunctionName = Names.getSimpleName(functionName);
    final MethodSymbol functionSymbol = new MethodSymbol(simpleFunctionName);
    functionSymbol.setPackageName(packageName);
    return functionSymbol;
  }

  public static List<MethodSymbol> getMethodSymbols() {
    return name2FunctionSymbol.values().stream().map(MethodSymbol::new).collect(toList());
  }

  public static Optional<MethodSymbol> getMethodSymbolIfExists(final String methodName) {
    if (name2FunctionSymbol.containsKey(methodName)) {
      return Optional.of(name2FunctionSymbol.get(methodName));
    }
    else {
      return Optional.empty();
    }

  }


}
