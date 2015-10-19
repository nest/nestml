/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest;

import de.se_rwth.commons.logging.Log;
import org.junit.BeforeClass;

/**
 * TODO
 *
 * @author plotnikov
 */
public class DisableFailQuickMixin {
  @BeforeClass
  public static void disableFailQuick() {
    Log.enableFailQuick(false);
  }
}
