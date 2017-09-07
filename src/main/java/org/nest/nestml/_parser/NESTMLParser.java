/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._parser;

import com.google.common.collect.Lists;
import com.google.common.io.Files;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.antlr.v4.runtime.RecognitionException;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._visitor.UnitsSIVisitor;
import org.nest.utils.AstUtils;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.List;
import java.util.Optional;

/**
 * HW parser that also is able
 *
 * @author plotnikov
 */
public class NESTMLParser extends NESTMLParserTOP {
  private final List<String> sourceText = Lists.newArrayList();

  @Override
  public Optional<ASTNESTMLCompilationUnit> parseNESTMLCompilationUnit(final String filename)
      throws IOException, RecognitionException {

    final Optional<ASTNESTMLCompilationUnit> res = super.parseNESTMLCompilationUnit(filename);

    if (res.isPresent()) {
      res.get().setArtifactName(Files.getNameWithoutExtension(filename));
      // in case of no importstatements the first comment, that should belong to neuron, is interpreted as artifact
      // comment
      forwardModelComment(res.get());

      final List<Finding> typeFindings = UnitsSIVisitor.convertSiUnitsToSignature(res.get());
      if (!typeFindings.isEmpty()) {
        Log.error("The modelfile contains semantic errors with respect to SI units.");
        Log.error(String.format("There are %d errors", typeFindings.size()));
        return Optional.empty();
      }

      // store model text as list of strings
      sourceText.addAll(Files.readLines(new File(filename), Charset.defaultCharset()));
      final List<ASTDeclaration> declarations = AstUtils.getAll(res.get(), ASTDeclaration.class);

      for (final ASTDeclaration astDeclaration:declarations) {
        int line = astDeclaration.get_SourcePositionStart().getLine();
        final List<String> variableComments = extractComments(sourceText, line - 1);
        variableComments.forEach(astDeclaration::addDocString);
      }

    }

    return res;
  }

  /**
   * Extracts comments starting from the `line` backwards
   */
  private List<String> extractComments(final List<String> sourceText, int lineIndex) {
    final List<String> result = Lists.newArrayList();
    String DOC_STRING_START = "##";
    if (sourceText.get(lineIndex).contains(DOC_STRING_START)) {
      result.add(sourceText.get(lineIndex).substring(sourceText.get(lineIndex).indexOf(DOC_STRING_START)).trim());
    }

    int searchBackIndex = lineIndex - 1;
    while (searchBackIndex > 0) {
      final String currentLine = sourceText.get(searchBackIndex);
      if (currentLine.trim().startsWith(DOC_STRING_START)) {
        result.add(0, currentLine.substring(currentLine.indexOf(DOC_STRING_START)).trim());
      }
      else {
        break;
      }
      --searchBackIndex;
    }

    int searchForwardIndex = lineIndex + 1;
    while (searchForwardIndex < sourceText.size()) {
      final String currentLine = sourceText.get(searchForwardIndex);
      if (currentLine.trim().startsWith(DOC_STRING_START)) {
        result.add(currentLine.substring(currentLine.indexOf(DOC_STRING_START) + 1).trim());
      }
      else {
        break;
      }
      ++searchForwardIndex;
    }
    return result;
  }

  /**
   * Through the grammar structure it is not possible to distinguish between module comment and a comment on first
   * neuron. As a workaround put this comment also to the first neuron.
   */
  private void forwardModelComment(final ASTNESTMLCompilationUnit root) {
    if (!root.get_PreComments().isEmpty() && !root.getNeurons().isEmpty()) {
      final ASTNeuron astNeuron = root.getNeurons().get(0);
      astNeuron.set_PreComments(Lists.newArrayList(root.get_PreComments()));
      // copy of the list was necessary, since otherwise the list would be cleared in both nodes!
      root.get_PreComments().clear();

    }

  }

}
