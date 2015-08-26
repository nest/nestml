/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.CommonModelNameCalculator;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.SymbolKind;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.se_rwth.commons.Names;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.*;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Strings.isNullOrEmpty;
import static java.util.Optional.empty;

/**
 * Frontend for the Simple Programming Language (SPL)
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLLanguage extends NESTMLLanguageTOP {

  public static final String FILE_ENDING = "nestml";

  final PredefinedTypesFactory typesFactory;

  /**
   * {@inheritDoc}
   */
  public NESTMLLanguage(final PredefinedTypesFactory typesFactory) {
    super("NESTML Language", FILE_ENDING);
    this.typesFactory = typesFactory;

    addResolver(CommonResolvingFilter.create(NESTMLNeuronSymbol.class, NESTMLNeuronSymbol.KIND));
    addResolver(CommonResolvingFilter.create(NESTMLTypeSymbol.class, NESTMLTypeSymbol.KIND));
    addResolver(CommonResolvingFilter.create(NESTMLMethodSymbol.class, NESTMLMethodSymbol.KIND));
    addResolver(CommonResolvingFilter.create(NESTMLVariableSymbol.class, NESTMLVariableSymbol.KIND));
    addResolver(CommonResolvingFilter.create(NESTMLUsageSymbol.class, NESTMLUsageSymbol.KIND));

    setModelNameCalculator(new CommonModelNameCalculator() {
      @Override public Optional<String> calculateModelName(String name, SymbolKind kind) {
        if (kind.isKindOf(NESTMLNeuronSymbol.KIND)) {
          return Optional.of(calculateModelName(name));
        }
        else {
          return empty();
        }
      }

      /**
       * Neuron Models are placed in a file. The neuron which are defined in them are resolved by their names, but there is
       * no artifact for it, but neuron is defined in a file defined by the fqn prefix.
       * TODO: it is a big hack for now! wait for the correct implementation in the ST infrastructure
       */
      public String calculateModelName(String name) {
        checkArgument(!isNullOrEmpty(name));

        // a.b.nestmlfile.IaFNeuron => a.b.nestmlfile is the artifact name
        if (isQualifiedName(name)) {
          // each model must be loaded at most once. cache every candidate and return for ever subsequent call an invalid
          // name
          return Names.getQualifier(name);
        }

        return name;
      }

      private boolean isQualifiedName(String name) {
        return name.contains(".");
      }
    });
  }

  /**
   * {@inheritDoc}
   */
  @Override
  protected NESTMLModelLoader provideModelLoader() {
    return new NESTMLModelLoader(this);
  }

  @Override
  public Optional<CommonNESTMLSymbolTableCreator> getSymbolTableCreator(
      ResolverConfiguration resolverConfiguration, MutableScope mutableScope) {
    return Optional.of(new CommonNESTMLSymbolTableCreator(resolverConfiguration, mutableScope, new PredefinedTypesFactory()));
  }

}
