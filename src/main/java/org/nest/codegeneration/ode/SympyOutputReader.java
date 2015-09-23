package org.nest.codegeneration.ode;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Created by user on 20.05.15.
 */
public class SympyOutputReader {

  public List<String> readMatrixElementsFromFile(final String filename) {
    List<String> matrixElements;
    try {
      matrixElements = Files.lines(new File(filename).toPath())
          .filter(line -> !line.isEmpty())
          .collect(Collectors.toList());
      return matrixElements;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot find or read the file with propagator matrix.", e);
    }

  }

}
