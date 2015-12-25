/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Maps;
import de.se_rwth.commons.Names;
import org.nest.symboltable.symbols.MethodSymbol;

import java.util.Map;
import java.util.Set;

/**
 * Defines a set with implicit type functions, like {@code print, pow, ...}
 *
 * @author plotnikov
 */
public class PredefinedFunctionFactory {

  private static final String TIME_RESOLUTION = "resolution";
  private static final String TIME_STEPS = "steps";
  private static final String EMIT_SPIKE = "emitSpike";
  private static final String PRINT = "print";
  private static final String PRINTLN = "println";
  private static final String POW = "pow";
  private static final String EXP = "exp";
  private static final String LOGGER_INFO = "Logger.info";
  private static final String RANDOM = "random";
  private static final String RANDOM_INT = "randomInt";
  private static final String EXPM1 = "expm1";

  private final Map<String, MethodSymbol> name2FunctionSymbol = Maps.newHashMap();

  public PredefinedFunctionFactory() {

    final MethodSymbol timeSteps = createFunctionSymbol(TIME_STEPS);
    timeSteps.addParameterType(PredefinedTypes.getType("ms"));
    timeSteps.setReturnType(PredefinedTypes.getIntegerType());
    name2FunctionSymbol.put(TIME_STEPS, timeSteps);

    final MethodSymbol emitSpike = createFunctionSymbol(EMIT_SPIKE);
    emitSpike.setReturnType(PredefinedTypes.getRealType());
    name2FunctionSymbol.put(EMIT_SPIKE, emitSpike);

    // create
    final MethodSymbol printMethod = createFunctionSymbol(PRINT);
    printMethod.addParameterType(PredefinedTypes.getStringType());
    printMethod.setReturnType(PredefinedTypes.getVoidType());
    name2FunctionSymbol.put(PRINT, printMethod);

    final MethodSymbol printlnMethod = createFunctionSymbol(PRINTLN);
    printlnMethod.setReturnType(PredefinedTypes.getVoidType());
    name2FunctionSymbol.put(PRINTLN, printlnMethod);

    final MethodSymbol powMethod = createFunctionSymbol(POW);
    powMethod.addParameterType(PredefinedTypes.getRealType()); // base
    powMethod.addParameterType(PredefinedTypes.getRealType()); // exp
    powMethod.setReturnType(PredefinedTypes.getRealType());
    name2FunctionSymbol.put(POW, powMethod);

    final MethodSymbol expMethod = createFunctionSymbol(EXP);
    expMethod.addParameterType(PredefinedTypes.getRealType()); // base
    expMethod.setReturnType(PredefinedTypes.getRealType());
    name2FunctionSymbol.put(EXP, expMethod);

    final MethodSymbol loggerInfoMethod = createFunctionSymbol(LOGGER_INFO);
    loggerInfoMethod.addParameterType(PredefinedTypes.getStringType());
    loggerInfoMethod.setReturnType(PredefinedTypes.getVoidType());
    name2FunctionSymbol.put(LOGGER_INFO, loggerInfoMethod);

    final MethodSymbol randomMethod = createFunctionSymbol(RANDOM);
    randomMethod.setReturnType(PredefinedTypes.getRealType());
    name2FunctionSymbol.put(RANDOM, randomMethod);

    final MethodSymbol randomIntMethod = createFunctionSymbol(RANDOM_INT);
    randomIntMethod.setReturnType(PredefinedTypes.getIntegerType());
    name2FunctionSymbol.put(RANDOM_INT, randomIntMethod);

    final MethodSymbol timeResolution = createFunctionSymbol(TIME_RESOLUTION);
    timeResolution.setReturnType(PredefinedTypes.getRealType());
    name2FunctionSymbol.put(TIME_RESOLUTION, timeResolution);

    final MethodSymbol expm1 = createFunctionSymbol(EXPM1);
    expm1.addParameterType(PredefinedTypes.getRealType());
    expm1.setReturnType(PredefinedTypes.getRealType());
    name2FunctionSymbol.put(EXPM1, expm1);

  }

  private static MethodSymbol createFunctionSymbol(final String functionName) {
    final String packageName = Names.getQualifier(functionName);
    final String simpleFunctionName = Names.getSimpleName(functionName);
    final MethodSymbol functionSymbol = new MethodSymbol(simpleFunctionName);
    functionSymbol.setPackageName(packageName);
    return functionSymbol;
  }

  public Set<MethodSymbol> getMethodSymbols() {
    return ImmutableSet.copyOf(name2FunctionSymbol.values());
  }

}
