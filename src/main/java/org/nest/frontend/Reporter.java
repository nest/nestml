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

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;

import java.io.PrintStream;
import java.util.List;
import java.util.Optional;

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
  // Key: addNeuronReport name, value: info message
  private final List<Report> artifactReports = Lists.newArrayList();

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


  void reportProgress(final String message) {
    System.out.println(message);
  }

  void addSystemInfo(final String message, final Level level) {
    systemReports.add(level + ": " + message);
    System.out.println(level + ": " + message);
  }



  void printReports(final PrintStream info, final PrintStream err) {
    Optional<Report> error = artifactReports
        .stream()
        .filter(message -> message.severity.equals(Level.ERROR))
        .findAny();

    info.println("----------------------------------------------------------");
    info.println("-----------------Execution summary------------------------");
    systemReports.forEach(report -> printSystemError(report, info, err));
    error.ifPresent(errorMessage -> err.println("ERROR: Code generation was canceled."));

    info.println("-----------------Neurons---------------------------------");
    artifactReports.forEach(entry -> printEntry(entry, info, err));

    info.println("-----------------Statistics ------------------------------");
    info.println("Overall " + artifactReports.size() + " NESTML artifact(s) found and processed");
    info.println("----------------------------------------------------------");

  }

  private void printSystemError(
      final String report,
      final PrintStream info,
      final PrintStream err) {
    if (report.startsWith(Level.ERROR.toString())) {
      info.println(report);
    }
    else {
      err.println(report);
    }

  }

  private void printEntry(
      final Report report,
      final PrintStream info,
      final PrintStream err) {
    if (report.severity.equals(Level.ERROR)) {
      info.println(report.toString());
    }
    else {
      err.println(report.toString());
    }

  }

  void addNeuronReports(
      final String filename,
      final String neuronName,
      final List<Finding> messages) {
    messages.forEach(finding -> addNeuronReport(
        filename,
        neuronName,
        finding));
  }

  void addNeuronReport(
      final String filename,
      final String neuronName,
      final Finding finding) {
    addNeuronReport(
        filename,
        neuronName,
        convert(finding.getType()),
        getCode(finding.getMsg()),
        finding.getSourcePosition().isPresent()?finding.getSourcePosition().get().getLine():0,
        finding.getSourcePosition().isPresent()?finding.getSourcePosition().get().getColumn():0,
        finding.getMsg());
  }

  void addNeuronReport(
      final String filename,
      final String neuronName,
      final Level severity,
      final String code,
      final Integer row,
      final Integer col,
      final String message) {
    final Report report = new Report(
        filename,
        neuronName,
        severity,
        code,
        row,
        col,
        message);
    artifactReports.add(report);
  }

  private String getCode(final String msg) {
    final String[] tokens = msg.split(" ");

    if (tokens.length == 0) {
      return "";
    }
    else {
      return tokens[0];
    }

  }

  private Level convert(Finding.Type type) {
    switch (type){
      case WARNING:
        return Level.WARNING;
      case ERROR:
        return Level.ERROR;
      default:
        return Level.INFO;
    }

  }

  public String toJson() {
    return "";
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

  static class Report {
    final String filename;
    final String neuronName;
    final Level severity;
    final String code;
    final Integer row;
    final Integer col;
    final String message;

    Report(
        final String filename,
        final String neuronName,
        final Level severity,
        final String code,
        final Integer row,
        final Integer col,
        final String message) {
      this.filename = filename;
      this.neuronName = neuronName;
      this.severity = severity;
      this.code = code;
      this.row = row;
      this.col = col;
      this.message = message;
    }

    @Override
    public String toString() {
      return severity + ": " +  filename + " <" + row + "," + col + "> :" + message;
    }
  }

}
