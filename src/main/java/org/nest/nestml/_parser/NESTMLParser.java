/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._parser;

import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.antlr.v4.runtime.RecognitionException;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

/**
 * HW parser that also is able
 *
 * @author plotnikov
 */
public class NESTMLParser extends NESTMLParserTOP {

  private final Optional<Path> modelPath;

  public NESTMLParser() {
    modelPath = Optional.empty();
  }

  public NESTMLParser(final Path modelPath) {
    this.modelPath = Optional.of(modelPath);
  }


  @Override
  public Optional<ASTNESTMLCompilationUnit> parseNESTMLCompilationUnit(String filename)
      throws IOException, RecognitionException {
    final Path pathToModel = Paths.get(filename).normalize();
    if (pathToModel.getParent() == null) {
      final String msg = String.format("The model '%s' must be stored in a folder. Structuring "
          + "models improves maintenance.", filename);
      Log.error(msg);
      return Optional.empty();
    }
    if (!filename.endsWith(".nestml")) {
      Log.error("NESTML models must be stored in artifacts with '.nestml' file extension.");
      return Optional.empty();
    }

    final Optional<ASTNESTMLCompilationUnit> res = super.parseNESTMLCompilationUnit(filename);
    if (res.isPresent()) {
      if (modelPath.isPresent()) {
        final Optional<String> packageName = computePackageName(Paths.get(filename), modelPath.get());
        final String artifactName = computeArtifactName(Paths.get(filename));

        if (packageName.isPresent()) {
          res.get().setPackageName(packageName.get());
        }
        res.get().setArtifactName(artifactName);
      }
      else {
        if (filename.endsWith(".nestml")) {

          final String withoutFileExt = filename.substring(0, filename.indexOf(".nestml"));
          final String filenameAsPackage = Names.getPackageFromPath(withoutFileExt);
          final String packageName = Names.getQualifier(filenameAsPackage);
          final String artifactName = Names.getSimpleName(filenameAsPackage);

          res.get().setPackageName(packageName);
          res.get().setArtifactName(artifactName);
        }
        else {
          Log.warn("Parser doesn't set the package and artifact name.");
        }

      }

    }

    return res;
  }

  protected Optional<String> computePackageName(Path artifactPath, Path modelPath) {
    artifactPath = artifactPath.normalize().toAbsolutePath();
    modelPath = modelPath.normalize().toAbsolutePath();
    final Path directParent = modelPath.relativize(artifactPath).getParent();
    if (directParent == null) {
      return Optional.empty();
    }
    else {
      final String pathAsString = directParent.toString();
      return Optional.of(Names.getPackageFromPath(pathAsString));
    }

  }

  protected String computeArtifactName(final Path artifactPath) {
    final String filename = artifactPath.getFileName().getName(0).toString();
    if (filename.endsWith(".nestml")) {
      return filename.substring(0, filename.indexOf(".nestml"));
    } else {
      return filename;
    }

  }
}
