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
@SuppressWarnings({"unused"})
public class ASTBuffers {

  private final NESTML2NESTTypeConverter nestml2NESTTypeConverter;

  public ASTBuffers() {
    nestml2NESTTypeConverter = new NESTML2NESTTypeConverter();
  }

  public static boolean isInhibitory(final ASTInputLine buffer) {
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

  public static boolean isExcitatory(final ASTInputLine buffer) {
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

  public String printBufferGetter(VariableSymbol buffer, boolean isInStruct) {
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

  public String printBufferArrayGetter(final VariableSymbol buffer) {
    if (buffer.isSpikeBuffer() && buffer.isInhAndExc()) {

      return "inline " + nestml2NESTTypeConverter.convert(buffer.getType()) + "&" +
             " get_" + buffer.getName() + "() {" +
             "  return spike_inputs_[" + buffer.getName().toUpperCase() + " - 1]; " +
             "}";
    }
    else {
      return printBufferGetter(buffer, true);
    }
  }

  public String printBufferDeclaration(final ASTInputLine astInputLine) {
    checkArgument(astInputLine.getEnclosingScope().isPresent(), "Run symboltable creator!");
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

    return "//!< Buffer incoming " + buffer.getType().getName() + "s through delay, as sum\n" +
           bufferType + " " + buffer.getName();

  }

  public String printBufferDeclarationValue(final VariableSymbol buffer) {
    if (buffer.getVectorParameter().isPresent()) {
      return "std::vector< double > " + Names.bufferValue(buffer);
    }
    else {

      return "double " + Names.bufferValue(buffer);
    }
  }

  public String printBufferInitialization(final VariableSymbol buffer) {
    return "get_" + buffer.getName() + "().clear(); //includes resize";
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
