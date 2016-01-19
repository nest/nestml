/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._parser;

import de.se_rwth.commons.Names;
import org.antlr.v4.runtime.RecognitionException;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;

/**
 * HW Parser that is responsible for the computation of the package and module
 *
 * @author plotnikov
 */
public class NESTMLParser extends NESTMLParserTOP {
  @Override
  public Optional<ASTNESTMLCompilationUnit> parseNESTMLCompilationUnit(String filename)
      throws IOException, RecognitionException {

    final Optional<ASTNESTMLCompilationUnit> res = super.parseNESTMLCompilationUnit(filename);
    if (res.isPresent()) {
      final String packageName = Names.getPackageFromPath(filename);
    }
    return res;
  }

  protected String computePackage(final Path modelPath, final Path absoluteFilePath) {
    return absoluteFilePath.relativize(modelPath).getParent().toString();
  }

  protected String computeArtifact(final Path absoluteFilePath) {
    final String filename = absoluteFilePath.getFileName().toString();
    if (filename.endsWith(".nestml")) {
      return filename.substring(0, filename.indexOf(".nestml"));
    }
    return absoluteFilePath.getFileName().toString();
  }

}
