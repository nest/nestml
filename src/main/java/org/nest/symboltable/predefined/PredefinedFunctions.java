/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Maps;
import de.se_rwth.commons.Names;
import org.nest.symboltable.symbols.MethodSymbol;

import java.util.Map;
import java.util.Set;

import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * Defines a set with implicit type functions, like {@code print, pow, ...}
 *
 * @author plotnikov
 */
public class PredefinedFunctions {

  public static final String TIME_RESOLUTION = "resolution";
  public static final String TIME_STEPS = "steps";
  public static final String EMIT_SPIKE = "emitSpike";
  public static final String PRINT = "print";
  public static final String PRINTLN = "println";
  public static final String POW = "pow";
  public static final String EXP = "exp";
  public static final String LOGGER_INFO = "info";
  public static final String LOGGER_WARNING = "warning";
  public static final String RANDOM = "random";
  public static final String RANDOM_INT = "randomInt";
  public static final String EXPM1 = "expm1";
  public static final String INTEGRATE = "integrate";


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

    final MethodSymbol integrate = createFunctionSymbol(INTEGRATE);
    integrate.addParameterType(getRealType());
    integrate.setReturnType(getVoidType());
    name2FunctionSymbol.put(INTEGRATE, integrate);
  }

  private static MethodSymbol createFunctionSymbol(final String functionName) {
    final String packageName = Names.getQualifier(functionName);
    final String simpleFunctionName = Names.getSimpleName(functionName);
    final MethodSymbol functionSymbol = new MethodSymbol(simpleFunctionName);
    functionSymbol.setPackageName(packageName);
    return functionSymbol;
  }

  public static Set<MethodSymbol> getMethodSymbols() {
    return ImmutableSet.copyOf(name2FunctionSymbol.values());
  }

  public static MethodSymbol getMethodSymbol(final String methodName) {
    Preconditions.checkArgument(name2FunctionSymbol.containsKey(methodName));
    return name2FunctionSymbol.get(methodName);
  }

}
