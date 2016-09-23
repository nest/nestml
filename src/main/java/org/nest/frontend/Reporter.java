/*
 * Reporter.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.frontend;

import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.Lists;
import com.google.common.collect.Multimap;
import de.se_rwth.commons.logging.Finding;

import java.io.PrintStream;
import java.util.List;
import java.util.Map;

/**
 * Collects all finding and statuses for artifacts and containing neurons.
 *
 * @implSpec Not parallelizable, but the frontend is executed with one instance.
 * @author plotnikov
 */
class Reporter {
  // Not parallelizable, but the frontend is executed with one instance.
  static private Reporter reporter = new Reporter();

  private final List<String> systemReports = Lists.newArrayList();
  // Key: addArtifactInfo name, value: info message
  private final Multimap<String, String> artifactReports = ArrayListMultimap.create();

  /**
   * Use the factory method
   */
  private Reporter() {

  }

  /**
   *
   * @return the instance of the reporter
   */
  public static Reporter get() {
    return reporter;
  }

  void addSystemInfo(final String message, final Level level) {
    systemReports.add(level + ": " + message);
  }

  void addArtifactInfo(final String artifactName, final String message, final Level level) {
    artifactReports.put(artifactName, level + ": " + message);
  }

  void printReports(final PrintStream info, final PrintStream err) {
    info.println("-----------------Environment summary----------------------");
    systemReports.forEach(report -> printEntry(report, info, err));
    info.println("-----------------Artifact summary-------------------------");
    artifactReports.entries().forEach(entry -> printEntry(entry, info, err));
    info.println("Overall " + artifactReports.entries().size() + " NESTML artifacts found and processed");
  }

  private void printEntry(final String message, final PrintStream info, final PrintStream err) {
    if (message.startsWith(Level.INFO.text)) {
      info.println(message);
    }
    else {
      err.println(message);
    }

  }

  private void printEntry(
      final Map.Entry<String, String> entry,
      final PrintStream info,
      final PrintStream err) {
    if (entry.getValue().startsWith(Level.INFO.text)) {
      info.println(entry.getKey() + " : " + entry.getValue());
    }
    else {
      err.println(entry.getKey() + " : " + entry.getValue());
    }

  }

  void addArtifactFindings(final String artifactName, final List<Finding> messages) {
    messages.forEach(finding -> addArtifactInfo(
        artifactName,
        finding.getMsg(),
        finding.getType().equals(Finding.Type.ERROR)?Level.ERROR:Level.WARNING));
  }


  enum Level {
    INFO("INFO"), WARNING("WARNING"), ERROR("ERROR");

    private final String text;

    Level(final String text) {
      this.text = text;
    }

    @Override
    public String toString() {
      return text;
    }

  }

}
