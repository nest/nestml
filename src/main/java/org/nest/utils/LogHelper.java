/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import com.google.common.collect.Lists;
import de.monticore.cocos.CoCoFinding;
import de.monticore.cocos.CoCoLog;

import java.util.Collection;

/**
 * Provides convenient method to work with error messages coming from {@code Log}.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class LogHelper {
  /**
   *
   * @return Number of {@code errorCode}s occurrences in {@code findings}
   */
  public static Integer countOccurrences(String errorCode, Collection<CoCoFinding> findings) {
    Long occurrences = findings.stream().filter(error -> error.getCode().equals(errorCode)).count();
    // it is unlikely that the number of issues is greater than the domain of int!    Integer result = 0;
    return safeLongToInt(occurrences);

  }

  /**
   *
   * @return Number of {@code errorCode}s occurrences in {@code findings}
   */
  public static Integer countOccurrencesByPrefix(String errorCode, Collection<CoCoFinding> findings) {
    Long occurrences = findings.stream().filter(error -> error.getCode().startsWith(errorCode)).count();
    // it is unlikely that the number of issues is greater than the domain of int!    Integer result = 0;
    return safeLongToInt(occurrences);

  }


  /**
   *
   * @return Number of {@code errorCode}s occurrences in {@code findings}
   */
  public static Collection<String> getFindingsByPrefix(String prefix, Collection<CoCoFinding> findings) {
    final Collection<String> result = Lists.newArrayList();
    findings.forEach(e -> {
      if (e.getCode().startsWith(prefix)) {
        result.add(e.getCode() + ":" + e.getMsg() + ":" + e.getSourcePosition());
      }
    });
    // it is unlikely that the number of issues is greater than the domain of int!    Integer result = 0;
    return result;

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
}
