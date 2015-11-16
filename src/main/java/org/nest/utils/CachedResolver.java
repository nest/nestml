package org.nest.utils;

import com.google.common.collect.Maps;
import de.monticore.symboltable.Scope;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

import java.util.Map;
import java.util.Optional;

/**
 * Resolves the symbol by name if not already resolved.
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 * @since 0.0.1
 */
public class CachedResolver {
  private static final String LOG_NAME = CachedResolver.class.getName();
  final Map<String, NESTMLTypeSymbol> cache = Maps.newHashMap();

  /**
   * Resolves the symbol by name if not already resolved.
   */
  public Optional<NESTMLTypeSymbol> resolveAndCache(Scope scope, String typeName) {
    if (cache.containsKey(typeName)) {
      Log.trace("Uses the cached symbol version: " + typeName, LOG_NAME);
      return Optional.of(cache.get(typeName));
    }
    else {
      Optional<NESTMLTypeSymbol> typeSymbol = scope.resolve(typeName, NESTMLTypeSymbol.KIND);
      if (typeSymbol.isPresent()) {
        cache.put(typeName, typeSymbol.get());
      }
      return typeSymbol;
    }

  }
}
