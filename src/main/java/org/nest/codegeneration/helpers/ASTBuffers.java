/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.helpers;

import de.monticore.symboltable.Scope;
import org.nest.codegeneration.converters.NESTML2NESTTypeConverter;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTInputType;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;

/**
 * Provides methods to print beffer parameter
 * grammar:
 *
 *   InputLine =
 *     Name
 *     ("[" sizeParameter:Name "]")?
 *     "<-" InputType*
 *     (["spike"] | ["current"]);
 *     InputType = (["inhibitory"] | ["excitatory"]);
 *
 * @author plotnikov
 */
@SuppressWarnings("unused")
public class ASTBuffers {

  private final NESTML2NESTTypeConverter nestml2NESTTypeConverter;

  public ASTBuffers() {
    nestml2NESTTypeConverter = new NESTML2NESTTypeConverter();
  }

  public boolean isInhibitory(final ASTInputLine buffer) {
    boolean isInhibitory = false, isExcitatory = false;
    for (final ASTInputType inputType : buffer.getInputTypes()) {
      if (inputType.isInhibitory()) {
        isInhibitory = true;
      }
      if (inputType.isExcitatory()) {
        isExcitatory = true;
      }
    }
    // defulat
    return !isInhibitory && !isExcitatory || isInhibitory;

  }

  public boolean isExcitatory(final ASTInputLine buffer) {
    boolean isInhibitory = false, isExcitatory = false;
    for (final ASTInputType inputType : buffer.getInputTypes()) {
      if (inputType.isInhibitory()) {
        isInhibitory = true;
      }
      if (inputType.isExcitatory()) {
        isExcitatory = true;
      }
    }
    // default
    return !isInhibitory && !isExcitatory || isExcitatory;
  }

  public String printBufferGetter(final ASTInputLine astInputLine, boolean isInStruct) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final VariableSymbol buffer = VariableSymbol.resolve(astInputLine.getName(), scope);

    return printBufferGetter(buffer, isInStruct);
  }

  private String printBufferGetter(VariableSymbol buffer, boolean isInStruct) {
    final StringBuilder functionDeclaration = new StringBuilder();
    functionDeclaration.append("inline ");

    if (buffer.getVectorParameter().isPresent()) {
      functionDeclaration.append("std::vector< ");
      functionDeclaration.append(nestml2NESTTypeConverter.convert(buffer.getType()));
      functionDeclaration.append(" > &");
    }
    else {
      functionDeclaration.append(nestml2NESTTypeConverter.convert(buffer.getType()) + "&");
    }

    functionDeclaration.append(" get_"+buffer.getName() + "() {");

    if (isInStruct) {
      functionDeclaration.append("return " + buffer.getName() + "; ");
    }
    else {
      functionDeclaration.append("return B_.get_" + buffer.getName() + "(); ");
    }

    functionDeclaration.append("}");
    return functionDeclaration.toString();
  }

  public String printBufferArrayGetter(final ASTInputLine astInputLine) {
    if (astInputLine.isSpike() && ASTUtils.isInhExc(astInputLine)) {
      checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
      final Scope scope = astInputLine.getEnclosingScope().get();
      final VariableSymbol buffer = VariableSymbol.resolve(astInputLine.getName(), scope);

      final StringBuilder functionDeclaration = new StringBuilder();
      functionDeclaration.append("inline ");


      functionDeclaration.append(nestml2NESTTypeConverter.convert(buffer.getType()) + "&")
          .append(" get_" + astInputLine.getName() + "() {")
          .append("return spike_inputs_[" + astInputLine.getName().toUpperCase() + "]; ");

      functionDeclaration.append("}");
      return functionDeclaration.toString();
    }
    else {
      return printBufferGetter(astInputLine, true);
    }
  }



  public String printBufferDeclaration(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final VariableSymbol buffer = VariableSymbol.resolve(astInputLine.getName(), scope);

    return printBufferDeclaration(buffer);
  }

  public String printBufferDeclaration(VariableSymbol buffer) {
    String bufferType;
    if (buffer.getVectorParameter().isPresent()) {
      bufferType = "std::vector< " + nestml2NESTTypeConverter.convert(buffer.getType()) + " >";
    }
    else {
      bufferType  = nestml2NESTTypeConverter.convert(buffer.getType());
    }
    bufferType = bufferType.replace(".", "::"); // TODO review

    return bufferType + " " + buffer.getName() + ";" +
        "\n//!< Buffer incoming " + buffer.getType().getName() + "s through delay, as sum\n";
  }

  public String printBufferInitialization(final ASTInputLine astInputLine) {
    return "get_" + astInputLine.getName() + "().clear(); //includes resize";
  }

  public String vectorParameter(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final VariableSymbol buffer = VariableSymbol.resolve(astInputLine.getName(), scope);
    checkState(buffer.getVectorParameter().isPresent(), "Cannot resolve the variable: " + astInputLine.getName());
    return buffer.getVectorParameter().get();
  }

  public boolean isVector(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "");
    final Scope scope = astInputLine.getEnclosingScope().get();
    final VariableSymbol buffer = VariableSymbol.resolve(astInputLine.getName(), scope);

    return buffer.getVectorParameter().isPresent();
  }
}
