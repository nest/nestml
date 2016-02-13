/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._symboltable.NESTMLLanguage;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.List;
import java.util.function.Predicate;

import static java.nio.file.FileSystems.getDefault;

/**
 * Provides base methods to work with model files: collect.
 *
 * @author plotnikov
 */
public class FileHelper {

  public static List<Path> collectNESTMLModelFilenames(final Path path) {
    final PathMatcher matcher = getDefault().getPathMatcher("glob:*." + NESTMLLanguage.FILE_ENDING);
    return FileHelper.collectFiles(path, modelFile -> matcher.matches(modelFile.getFileName()));
  }

  public static List<Path> collectFiles(
      final Path inputPath,
      final Predicate<Path> predicate) {
    final List<Path> filenames = Lists.newArrayList();
    try {
      Files.walkFileTree(inputPath, new SimpleFileVisitor<Path>() {
        @Override
        public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
          if (predicate.test(file)) {
            filenames.add(file);
          }
          return FileVisitResult.CONTINUE;
        }
      });
    }
    catch (IOException e) {
      final String msg = "Cannot collect NESTML models in:  " + inputPath;
      Log.error(msg, e);
      throw new RuntimeException(msg, e);
    }
    return filenames;
  }
}
