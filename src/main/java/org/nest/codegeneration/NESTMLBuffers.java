/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTInputType;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Todo: refactor
 * grammar:
 * {@code
 * InputLine = Name "<-" InputType* ([spike:"spike"]|[current:"current"]);
 * InputType = (["inhibitory"]|["excitatory"]);
 * }
 *
 * @author plotnikov
 * @since 0.0.1
 */
@SuppressWarnings("unused")
public class NESTMLBuffers {

  private final PredefinedTypesFactory typesFactory;

  private final NESTML2NESTTypeConverter nestml2NESTTypeConverter;

  public NESTMLBuffers(PredefinedTypesFactory typesFactory) {
    this.typesFactory = typesFactory;
    nestml2NESTTypeConverter = new NESTML2NESTTypeConverter(typesFactory);
  }
  public boolean isInhibitory(final ASTInputLine buffer) {
    boolean isInhibitory = false, isExcitatory = false;
    for (final ASTInputType inputType:buffer.getInputTypes()) {
      if (inputType.isInhibitory()) {
        isInhibitory = true;
      }
      if (inputType.isExcitatory()) {
        isExcitatory = true;
      }
    }
    if ( !isInhibitory && !isExcitatory ) { // defulat
      return true;
    } else {
      return isInhibitory;
    }

  }

  public boolean isExcitatory(final ASTInputLine buffer) {
    boolean isInhibitory = false, isExcitatory = false;
    for (final ASTInputType inputType:buffer.getInputTypes()) {
      if (inputType.isInhibitory()) {
        isInhibitory = true;
      }
      if (inputType.isExcitatory()) {
        isExcitatory = true;
      }
    }
    if ( !isInhibitory && !isExcitatory ) { // default
      return true;
    } else {
      return isExcitatory;
    }
  }
  public String printBufferGetter(final ASTInputLine astInputLine, boolean isInStruct) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final NESTMLVariableSymbol buffer = resolveVariable(astInputLine.getName(), scope);

    final StringBuilder functionDeclaration = new StringBuilder();
    functionDeclaration.append("inline ");

    if (buffer.getArraySizeParameter().isPresent()) {
      functionDeclaration.append("std::vector< ");
      functionDeclaration.append(nestml2NESTTypeConverter.convert(buffer.getType()));
      functionDeclaration.append(" > &");
    }
    else {
      functionDeclaration.append(nestml2NESTTypeConverter.convert(buffer.getType()) + "&");
    }

    functionDeclaration.append(" get_"+astInputLine.getName() + "() {");

    if (isInStruct) {
      functionDeclaration.append("return " + astInputLine.getName() + "_; ");
    }
    else {
      functionDeclaration.append("return B_.get_" + astInputLine.getName() + "(); ");
    }

    functionDeclaration.append("}");
    return functionDeclaration.toString();
  }

  public String printBufferDeclaration(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final NESTMLVariableSymbol buffer = resolveVariable(astInputLine.getName(), scope);

    String bufferType;
    if (buffer.getArraySizeParameter().isPresent()) {
      bufferType = "std::vector< " + nestml2NESTTypeConverter.convert(buffer.getType()) + " >";
    }
    else {
      bufferType  = nestml2NESTTypeConverter.convert(buffer.getType());
    }
    bufferType = bufferType.replace(".", "::"); // TODO review

    final StringBuilder bufferDeclaration = new StringBuilder();

    bufferDeclaration.append(bufferType).append(" ");
    bufferDeclaration.append(astInputLine.getName() + "_");
    bufferDeclaration.append("//!< Buffer incoming " + buffer.getType().getName() + "s through delay, as sum\n");

    return bufferDeclaration.toString();
  }

  public String printBufferTypesVariables(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");

    final StringBuilder declaration = new StringBuilder();
    declaration.append("std::vector<long> receptor_types_").append(astInputLine.getName());
    return declaration.toString();
  }

  public String printBufferInitialization(final ASTInputLine astInputLine) {
    return "get_" + astInputLine.getName() + "().clear(); //includes resize";
  }

  public String vectorParameter(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final NESTMLVariableSymbol buffer = resolveVariable(astInputLine.getName(), scope);
    checkState(buffer.getArraySizeParameter().isPresent(), "Cannot resolve the variable: " + astInputLine.getName());
    return buffer.getArraySizeParameter().get() + "_";
  }

  // TODO duplicate
  private NESTMLVariableSymbol resolveVariable(final String variableName, final Scope scope) {
    final Optional<NESTMLVariableSymbol> variableSymbol = scope.resolve(
        variableName, NESTMLVariableSymbol.KIND);
    checkState(variableSymbol.isPresent(), "Cannot resolve the variable: " + variableName);
    return variableSymbol.get();
  }

  public boolean isVector(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final NESTMLVariableSymbol buffer = resolveVariable(astInputLine.getName(), scope);

    return buffer.getArraySizeParameter().isPresent();
  }
}
