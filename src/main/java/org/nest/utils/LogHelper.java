/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import de.se_rwth.commons.logging.Finding;

import java.util.Collection;
import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Provides convenient method to work with error messages coming from {@code Log}.
 *
 * @author plotnikov
 */
public class LogHelper {

  /**
   *
   * @return Number of {@code error}s occurrences in {@code findings}
   */
  public static Integer countErrorsByPrefix(
      final String errorCode,
      final Collection<Finding> findings) {
    return countByPrefix(errorCode, Finding::isError, findings);
  }

  /**
   *
   * @return Number of {@code error}s occurrences in {@code findings}
   */
  public static Integer countWarningsByPrefix(
      final String errorCode,
      final Collection<Finding> findings) {
    return countByPrefix(errorCode, Finding::isWarning, findings);
  }

  /**
   *
   * @return Number of {@code errorType}s occurrences in {@code findings}
   */
  private static Integer countByPrefix(
      final String errorCode,
      final Predicate<Finding> errorType,
      final Collection<Finding> findings) {

    Long occurrences = findings.stream()
        .filter(errorType)
        .filter(error -> error.getMsg().startsWith(errorCode))
        .count();
    // it is unlikely that the number of issues is greater than the domain of int!    Integer result = 0;
    return toInt(occurrences);

  }


  /**
   * Converts long value to int under the conditions that the long value is representable
   * as an int.
   * @throws  IllegalArgumentException if the {@l} is greater than the biggest int
   */
  private static int toInt(long l) {
    if (l < Integer.MIN_VALUE || l > Integer.MAX_VALUE) {
      throw new IllegalArgumentException(l + " cannot be cast to int without changing its value.");
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

  public static Collection<Finding> getWarningsByPrefix(
      final String prefix,
      final List<Finding> findings) {
    return findings.stream()
        .filter(finding -> finding.getType().equals(Finding.Type.WARNING) && finding.getMsg().startsWith(prefix))
        .collect(Collectors.toList());
  }

}
