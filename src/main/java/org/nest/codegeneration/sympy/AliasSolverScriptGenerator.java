/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.base.Preconditions;
import de.monticore.generating.GeneratorEngine;
import de.monticore.generating.GeneratorSetup;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.spl._ast.ASTSPLNode;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static de.se_rwth.commons.logging.Log.info;
import static java.util.Optional.of;
import static org.nest.utils.ASTNodes.getVariableSymbols;

/**
 * Wrapps the logic how to generate a solver script to invert the alias definition.
 *
 * @author plotnikov
 */
public class AliasSolverScriptGenerator {

  private final static String LOG_NAME = AliasSolverScriptGenerator.class.getName();

  public static final String SCRIPT_GENERATOR_TEMPLATE = "org.nest.sympy.AliasSolver";

  public String getSolutionFile(final ASTAliasDecl astAliasDecl) {
    final String variableName = astAliasDecl.getDeclaration().getVars().get(0);
    return "alias" + variableName + ".expr";
  }

  public Optional<Path> generateAliasInverter(
      final ASTNeuron neuron,
      final Path outputDirectory) {
    final GeneratorSetup setup = new GeneratorSetup(new File(outputDirectory.toString()));

    final List<VariableSymbol> variables = getVariableSymbols(neuron);
    final List<VariableSymbol> aliases = variables
        .stream()
        .filter(VariableSymbol::isAlias)
        .collect(Collectors.toList());


    final Path generatedScriptFile = generateSolverScript(
        createGLEXConfiguration(),
        neuron,
        variables,
        aliases,
        setup);

    final String msg = String.format(
        "Successfully generated solver script for the aliases in : %s",
        neuron.getName());
    info(msg, LOG_NAME);

    return of(generatedScriptFile);
  }

  private static Path generateSolverScript(
      final GlobalExtensionManagement glex,
      final ASTNeuron neuron,
      final List<VariableSymbol> variables,
      final List<VariableSymbol> aliases,
      final GeneratorSetup setup) {

    setup.setGlex(glex);
    setup.setTracing(false); // python comments are not java comments
    setup.setCommentStart(Optional.of("#"));
    setup.setCommentEnd(Optional.empty());

    final GeneratorEngine generator = new GeneratorEngine(setup);

    final Path solverSubPath = Paths.get( "aliasSolver.py");

    final ExpressionsPrettyPrinter expressionsPrinter  = new ExpressionsPrettyPrinter();
    final List<VariableSymbol> dependentVariables = aliases
        .stream()
        .map(alias -> DependentVariableCalculator
            .getVariableSymbols(alias.getDeclaringExpression().get()))
        .collect(Collectors.toList());

    glex.setGlobalValue("printer", expressionsPrinter);
    glex.setGlobalValue("variables", variables);
    glex.setGlobalValue("aliases", aliases);
    glex.setGlobalValue("dependentVariables", dependentVariables);

    generator.generate(SCRIPT_GENERATOR_TEMPLATE, solverSubPath, neuron);

    return Paths.get(setup.getOutputDirectory().getPath(), solverSubPath.toString());
  }

  private static GlobalExtensionManagement createGLEXConfiguration() {
    return new GlobalExtensionManagement();
  }

  static class DependentVariableCalculator implements NESTMLVisitor {

    public VariableSymbol dependentVariable;

    public VariableSymbol getVariable() {
      return dependentVariable;
    }

    public static VariableSymbol getVariableSymbols(final ASTSPLNode astNode) {
      final DependentVariableCalculator calculator = new DependentVariableCalculator();
      astNode.accept(calculator);
      return calculator.getVariable();
    }

    @Override
    public void visit(final ASTQualifiedName astQualifiedName) {
      Preconditions.checkArgument(
          astQualifiedName.getEnclosingScope().isPresent(),
          "Run symbol table creator.");
      final Scope scope = astQualifiedName.getEnclosingScope().get();

      final String variableName = ASTNodes.toString(astQualifiedName);
      final Optional<VariableSymbol> variableSymbol
          = scope.resolve(variableName, VariableSymbol.KIND);
      if (variableSymbol.isPresent() && !variableSymbol.get().isAlias()) {
        dependentVariable = variableSymbol.get();
      }

    }

  }

}

