/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTOdeDeclaration;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.function.Function;

import static com.google.common.base.Preconditions.checkArgument;
import static java.util.stream.Collectors.toList;

/**
 * Takes SymPy result with the implicit form of ODEs (e.g replace shapes through a series of ODES) and replaces
 * the shapes through
 *
 * @author plotnikov
 */
public class ImplicitFormTransformer extends TransformerBase {
  public final static String EQUATIONS_FILE = "equations.tmp";
  private static final String DIFFERENTIATION_SIGN_PLACEHOLDER = "__D";

  private final Function<String, String> mapNameToOdeNotation = name -> name.replaceAll(DIFFERENTIATION_SIGN_PLACEHOLDER, "'");
  private final Function<String, String> variableNameExtracter = initialValue -> {
    final String variableNameRaw = initialValue.substring(0, initialValue.indexOf("_PSCInitialValue"));
    return mapNameToOdeNotation.apply(variableNameRaw);
  };

  private final Function<String, String> shapeNameExtracter = initialValue -> {
    final String variableNameRaw = initialValue.substring(0, initialValue.indexOf("_PSCInitialValue"));
    return variableNameRaw.replaceAll("__D", "");
  };

  public ASTNeuron transformToImplicitForm(
      final ASTNeuron astNeuron,
      final Path pscInitialValuesFile,
      final Path equationsFile) {
    checkArgument(astNeuron.getBody().getODEBlock().isPresent());

    ASTNeuron workingVersion = addDeclarationsToInternals(astNeuron, pscInitialValuesFile);
    workingVersion = replaceShapesThroughVariables(workingVersion);
    addUpdatesWithPSCInitialValue(
        pscInitialValuesFile,
        workingVersion.getBody(),
        variableNameExtracter,
        shapeNameExtracter);
    addEquationsToOdeBlock(equationsFile, astNeuron.getBody().getODEBlock().get());
    return workingVersion;
  }

  private void addEquationsToOdeBlock(final Path equationsFile, final ASTOdeDeclaration astOdeDeclaration) {
    try {
      final List<ASTEquation> equations = Files.lines(equationsFile)
          .map(NESTMLASTCreator::createEquation)
          .collect(toList());
      astOdeDeclaration.getODEs().addAll(equations);
    } catch (IOException e) {
      throw new RuntimeException("Cannot parse equations file.", e);
    }
  }

  private ASTNeuron replaceShapesThroughVariables(ASTNeuron astNeuron) {
    final List<ASTAliasDecl> stateVariablesDeclarations = shapesToStateVariables(astNeuron.getBody().getODEBlock().get());
    stateVariablesDeclarations.forEach(stateVariable -> astNeuron.getBody().addToStateBlock(stateVariable));
    astNeuron.getBody().getODEBlock().get().getShapes().clear();
    return astNeuron;
  }

  private List<ASTAliasDecl> shapesToStateVariables(final ASTOdeDeclaration astOdeDeclaration) {
    final List<String> stateVariables = astOdeDeclaration.getShapes()
        .stream()
        .map(shape -> shape.getLhs().toString())
        .collect(toList());

    return stateVariables
        .stream()
        .map(variable -> variable + " real")
        .map(NESTMLASTCreator::createAlias)
        .collect(toList());
  }

}
