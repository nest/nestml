/*
 * ReporterTest.java
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

import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.reporting.Reporter;

/**
 * @author plotnikov
 */
public class ReporterTest {

  @BeforeClass
  public static void setup() {
    final Reporter reporter = Reporter.get();

    reporter.addNeuronReport("iaf_neuron_artifact.nestml", "neuron_a", Reporter.Level.INFO, "NESTML_INFO_CODE", 0, 1, "This test info message1");
    reporter.addNeuronReport("iaf_neuron_artifact.nestml", "neuron_a", Reporter.Level.INFO, "NESTML_INFO_CODE", 0, 1, "This test info message2");
    reporter.addNeuronReport("iaf_neuron_artifact.nestml", "neuron_a", Reporter.Level.INFO, "NESTML_INFO_CODE", 0, 1, "This test info message3");
    reporter.addNeuronReport("iaf_neuron_artifact.nestml", "neuron_a", Reporter.Level.ERROR, "NESTML_ERROR_CODE", 0, 1, "This test error message1");
    reporter.addNeuronReport("iaf_neuron_artifact.nestml", "neuron_a", Reporter.Level.ERROR, "NESTML_ERROR_CODE", 0, 1, "This test error message2");
    reporter.addNeuronReport("iaf_neuron_artifact.nestml", "neuron_a", Reporter.Level.WARNING, "NESTML_WARNING_CODE", 0, 1, "This test error message2");

    reporter.reportProgress("Python is installed");
    reporter.reportProgress("Sympy is missing");

    reporter.addNeuronReport("iaf_neuron", "a", Reporter.Level.ERROR, "NESTML_A", 0, 1, "This test error message2");

  }

  @Test
  public void testPrint() {
    final Reporter reporter = Reporter.get();
    reporter.printReports(System.out, System.out);
  }

}