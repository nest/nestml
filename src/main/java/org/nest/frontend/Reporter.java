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

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;

import java.io.IOException;
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

  // Key: addNeuronReport name, value: info message
  private final List<Report> neuronReports = Lists.newArrayList();

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
    System.out.println(Level.INFO + ": " + message);
  }

  public String printFindingsAsJsonString() {
    try {
      ObjectMapper mapper = new ObjectMapper();
      final String jsonInString = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(neuronReports);
      System.out.println(jsonInString);

    }
    catch (IOException e) {
      e.printStackTrace();
    }
    return "";
  }

  void printReports(final PrintStream info, final PrintStream err) {
    Optional<Report> error = neuronReports
        .stream()
        .filter(message -> message.severity.equals(Level.ERROR))
        .findAny();

    info.println("----------------------------------------------------------");
    info.println("-----------------Execution summary------------------------");
    printFindingsAsJsonString();
    error.ifPresent(errorMessage -> err.println("ERROR: Code generation was canceled."));  }

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
        finding.getSourcePosition().isPresent()?finding.getSourcePosition().get().getLine():-1,
        finding.getSourcePosition().isPresent()?finding.getSourcePosition().get().getColumn():-1,
        getMessage(finding.getMsg()));
  }

  private String getMessage(final String msg) {
    final String[] tokens = msg.split(" : ");

    if (tokens.length >= 2) {
      return tokens[1];
    }
    else {
      return "NO_MESSAGE";
    }

  }

  private String getCode(final String msg) {
    final String[] tokens = msg.split(" : ");

    if (tokens.length == 0) {
      return "NESTML_ERROR : ";
    }
    else {
      return tokens[0];
    }

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
    neuronReports.add(report);
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
    public final String filename;
    public final String neuronName;
    public final Level severity;
    public final String code;
    public final Integer row;
    public final Integer col;
    public final String message;

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
      return severity + ": " +  filename + " at <" + row + "," + col + "> : " + message;
    }
  }

}
