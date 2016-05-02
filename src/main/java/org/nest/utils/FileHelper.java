/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._symboltable.NESTMLLanguage;
import org.nest.spl._symboltable.SPLLanguage;

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
  private static String LOG_NAME = FileHelper.class.getName();

  public static List<Path> collectNESTMLModelFilenames(final Path path) {
    final PathMatcher matcher = getDefault().getPathMatcher("glob:*." + NESTMLLanguage.FILE_ENDING);
    return FileHelper.collectFiles(path, modelFile -> matcher.matches(modelFile.getFileName()));
  }

  public static List<Path> collectSPLModelFilenames(final Path path) {
    final PathMatcher matcher = getDefault().getPathMatcher("glob:*." + SPLLanguage.FILE_ENDING);
    return FileHelper.collectFiles(path, modelFile -> matcher.matches(modelFile.getFileName()));
  }

  public static void deleteFilesInFolder(final Path file) {
    FileHelper.collectFiles(file, f -> true)
        .stream()
        .forEach(FileHelper::deleteFile);
  }

  public static void deleteFilesInFolder(final Path file, final Predicate<Path> predicate) {
    FileHelper.collectFiles(file, predicate)
            .stream()
            .forEach(FileHelper::deleteFile);
  }

  public static void deleteFile(final Path file) {
    try {
      Files.delete(file);
      Log.trace("Deleted  file: " + file.toString(), LOG_NAME);
    }
    catch (IOException e) {
      Log.error("Cannot delete file: " + file.toString(), e);
    }
  }

  public static void createFolders(final Path folder) {
    try {
      Files.createDirectories(folder);
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<Path> collectFiles(
      final Path inputPath,
      final Predicate<Path> predicate) {
    final List<Path> filenames = Lists.newArrayList();

    if (!Files.exists(inputPath)) {
      return filenames;
    }

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
