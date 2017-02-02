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

import org.junit.Test;

/**
 * @author plotnikov
 */
public class ReporterTest {

  @Test
  public void testPrint() {
    final Reporter reporter = Reporter.get();

    reporter.addArtifactInfo("iaf_neuron_artifact.nestml", "This test info message1", Reporter.Level.INFO);
    reporter.addArtifactInfo("iaf_neuron_artifact.nestml", "This test info message2", Reporter.Level.INFO);
    reporter.addArtifactInfo("iaf_neuron_artifact.nestml", "This test info message3", Reporter.Level.INFO);
    reporter.addArtifactInfo("iaf_neuron_artifact.nestml", "This test error message1", Reporter.Level.ERROR);
    reporter.addArtifactInfo("iaf_neuron_artifact.nestml", "This test error message2", Reporter.Level.ERROR);

    reporter.addSystemInfo("Python is installed", Reporter.Level.INFO);
    reporter.addSystemInfo("Sympy is missing", Reporter.Level.ERROR);

    reporter.addArtifactInfo("iaf_neuron", "This test error message2", Reporter.Level.ERROR);

    reporter.printReports(System.out, System.out);
    reporter.toJson();
  }

}