/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.sympy;

import com.google.common.collect.Lists;
import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.spl._ast.ASTOdeDeclaration;
import org.nest.utils.ASTNodes;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Wrapps the logic how to generateSympyODEAnalyzer C++ implementation from a NESTML model?
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 * @since 0.0.1
 */
public class ODE2SympyCodeGenerator {

  public static void generateSympyODEAnalyzer(GlobalExtensionManagement glex,
                                              ASTOdeDeclaration odeDeclaration,
                                              File outputDirectory,
                                              String neuronName) {
    final GeneratorSetup setup = new GeneratorSetup(outputDirectory);

    final ExpressionsPrettyPrinter expressionsPrettyPrinter = new ExpressionsPrettyPrinter();
    glex.setGlobalValue("sympy", odeDeclaration.getODEs());
    glex.setGlobalValue("eq", odeDeclaration.getEq());
    glex.setGlobalValue("expressionsPrettyPrinter", expressionsPrettyPrinter);
    expressionsPrettyPrinter.print(odeDeclaration.getODEs().getRhs());

    setup.setGlex(glex);
    setup.setTracing(false); // python comments are not java comments

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverFilePath = Paths.get(outputDirectory.getPath(), neuronName + "Solver.py");

    // TODO: filter out E
    final List<String> variables = filterConstantVariables(ASTNodes.getVariablesNamesFromAst(odeDeclaration));
    glex.setGlobalValue("variables", variables);

    // TODO: how do I find out the call was successful?
    generator.generate(
            "org.nest.sympy.SympySolver",
            solverFilePath,
            odeDeclaration);
  }

  /**
   * Filters mathematical constants like Pi, E, ...
   */
  private static List<String> filterConstantVariables(final List<String> variablesNames) {
    final List<String> result = Lists.newArrayList();
    result.addAll(variablesNames.stream().filter(variable -> !variable.equals("E"))
        .collect(Collectors.toList()));

    return result;
  }

}

