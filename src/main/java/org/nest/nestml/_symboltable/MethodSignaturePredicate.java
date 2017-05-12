/*
* Copyright (c) 2015 RWTH Aachen. All rights reserved.
*
* http://www.se-rwth.de/
*/
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolPredicate;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import java.util.ArrayList;
import java.util.List;

import static com.google.common.base.Strings.emptyToNull;
import static java.util.Objects.requireNonNull;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isReal;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;

public class MethodSignaturePredicate implements SymbolPredicate {

  private final String expectedMethodName;
  private final List<String> expectedParameterTypes = new ArrayList<>();

  public MethodSignaturePredicate(
      final String methodName,
      final List<String> parameters) {
    this.expectedMethodName = requireNonNull(emptyToNull(methodName));

    expectedParameterTypes.addAll(parameters);
  }

  @Override
  public boolean test(final Symbol symbol) {

    if ((symbol != null) && symbol.isKindOf(MethodSymbol.KIND) && (symbol instanceof MethodSymbol)) {
      final MethodSymbol methodSymbol = (MethodSymbol) symbol;

      if (methodSymbol.getName().equals(expectedMethodName) &&
          (methodSymbol.getParameterTypes().size() == expectedParameterTypes.size())) {
        for (int i=0; i < methodSymbol.getParameterTypes().size(); i++) {
          final String expectedType = expectedParameterTypes.get(i);
          final String actualType = methodSymbol.getParameterTypes().get(i).getFullName();

          //if both expected and actual are units and have the same base they are compatible
          boolean convertibleUnits = false;
          if(isUnit(getType(expectedType))&&isUnit(getType(actualType))){
            TypeSymbol expectedTypeSymbol = getType(expectedType);
            TypeSymbol actualTypeSymbol = getType(actualType);
            UnitRepresentation expectedTypeRep = UnitRepresentation.getBuilder().
                serialization(expectedTypeSymbol.getName()).build();
            UnitRepresentation actualTypeRep = UnitRepresentation.getBuilder().
                serialization(actualTypeSymbol.getName()).build();
            convertibleUnits = expectedTypeRep.equalBase(actualTypeRep);
          }

          if (!TypeChecker.isCompatible(actualType, expectedType) &&
              !(convertibleUnits)&&
              !(isUnit(methodSymbol.getParameterTypes().get(i)) && isReal(getType(expectedType))) &&
              !(isReal(methodSymbol.getParameterTypes().get(i)) && isUnit(getType(expectedType)))) {
            return false;
          }

        }

        return true;
      }

    }

    return false;
  }

}