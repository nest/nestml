/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import com.google.common.collect.Sets;
import de.monticore.CommonModelNameCalculator;
import de.monticore.symboltable.MutableScope;
import de.monticore.symboltable.ResolverConfiguration;
import de.monticore.symboltable.SymbolKind;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.se_rwth.commons.Names;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.symboltable.symbols.*;

import java.nio.file.Path;
import java.util.Optional;
import java.util.Set;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Strings.isNullOrEmpty;

/**
 * Frontend for the Simple Programming Language (SPL)
 *
 * @author plotnikov
 */
public class NESTMLLanguage extends NESTMLLanguageTOP {

  public static final String FILE_ENDING = "nestml";

  /**
   * {@inheritDoc}
   */
  public NESTMLLanguage() {
    super("NESTML Language", FILE_ENDING);

    addResolver(CommonResolvingFilter.create(NeuronSymbol.class, NeuronSymbol.KIND));

    addResolver(new PredefinedTypesFilter(TypeSymbol.class, TypeSymbol.KIND));

    addResolver(new PredefinedMethodsFilter(MethodSymbol.class, MethodSymbol.KIND));
    addResolver(CommonResolvingFilter.create(MethodSymbol.class, MethodSymbol.KIND));

    addResolver(CommonResolvingFilter.create(VariableSymbol.class, VariableSymbol.KIND));
    addResolver(new PredefinedVariablesFilter(VariableSymbol.class, VariableSymbol.KIND));

    addResolver(CommonResolvingFilter.create(UsageSymbol.class, UsageSymbol.KIND));

    setModelNameCalculator(new CommonModelNameCalculator() {

      @Override
      public Set<String> calculateModelNames(String name, SymbolKind kind) {
        if (kind.isKindOf(NeuronSymbol.KIND)) {
          return Sets.newHashSet(calculateModelName(name));
        }
        else {
          return Sets.newHashSet();
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

  @Override
  public NESTMLParser getParser() {
    return new NESTMLParser();
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
    return Optional.of(new CommonNESTMLSymbolTableCreator(resolverConfiguration, mutableScope));
  }

}
