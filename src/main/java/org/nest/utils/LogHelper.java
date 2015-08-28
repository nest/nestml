/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import de.se_rwth.commons.logging.Finding;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Provides convenient method to work with error messages coming from {@code Log}.
 *
 * @author plotnikov
 * @since 0.0.1
 */
public class LogHelper {
  /**
   *
   * @return Number of {@code errorCode}s occurrences in {@code findings}
   */
  public static Integer countErrorsByPrefix(String errorCode, Collection<Finding> findings) {

    Long occurrences = findings.stream()
        .filter(error -> error.getType().equals(Finding.Type.ERROR))
        .filter(error -> error.getMsg().startsWith(errorCode))
        .count();
    // it is unlikely that the number of issues is greater than the domain of int!    Integer result = 0;
    return safeLongToInt(occurrences);

  }

  /**
   * Converts long value to int under the conditions that the long value is representable
   * as an int.
   * @throws  IllegalArgumentException if the {@l} is greater than the biggest int
   */
  private static int safeLongToInt(long l) {
    if (l < Integer.MIN_VALUE || l > Integer.MAX_VALUE) {
      throw new IllegalArgumentException
              (l + " cannot be cast to int without changing its value.");
    }
    return (int) l;
  }

  public static Collection<Finding> getErrorsByPrefix(
      final String prefix,
      final List<Finding> findings) {
    return findings.stream()
        .filter(finding -> finding.getType().equals(Finding.Type.ERROR) && finding.getMsg().startsWith(prefix))
        .collect(Collectors.toList());
  }

}
