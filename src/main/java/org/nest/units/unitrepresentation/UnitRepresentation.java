package org.nest.units.unitrepresentation;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.google.common.base.Preconditions;

/**
 * @author ptraeder
 * Helper class. Controlled way of creating base representations of derived SI units.
 */

public class UnitRepresentation {
  private int magnitude;
  private int K,s,m,g,cd,mol,A;

  public void addMagnitude(int magnitude) {
    this.magnitude += magnitude;
  }

  public String toString() {
    int[] result = { K, s, m, g, cd, mol, A, magnitude };
    return Arrays.toString(result);
  }

  static public Optional<UnitRepresentation> lookupName(String unit){
    for (String pre: SIData.getSIPrefixes()){
      if(pre.regionMatches(false,0,unit,0,pre.length())){
        //See if remaining unit name matches a valid SI Unit. Since some prefixes are not unique
        String remainder = unit.substring(pre.length());
        if(SIData.getBaseRepresentations().containsKey(remainder)){
          int magnitude = SIData.getPrefixMagnitudes().get(pre);
          UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(remainder));
          result.addMagnitude(magnitude);
          return Optional.of(result);
        }
      }
    }if(SIData.getBaseRepresentations().containsKey(unit)) { //No prefix present, see if whole name matches
      UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(unit));
      return Optional.of(result);
    }
    //should never happen
    return Optional.empty();
  }

  public UnitRepresentation(int K, int s, int m, int g, int cd, int mol, int A, int magnitude) {
    this.K = K;
    this.s = s;
    this.m = m;
    this.g = g;
    this.cd = cd;
    this.mol = mol;
    this.A = A;
    this.magnitude = magnitude;
  }

  public UnitRepresentation(UnitRepresentation unit){
    this.K = unit.K;
    this.s = unit.s;
    this.m = unit.m;
    this.g = unit.g;
    this.cd = unit.cd;
    this.mol = unit.mol;
    this.A = unit.A;
    this.magnitude = unit.magnitude;
  }

  public UnitRepresentation(String serialized){
    Pattern parse = Pattern.compile("-?[0-9]+");
    Matcher matcher = parse.matcher(serialized);

    Preconditions.checkState(matcher.find());
    this.K = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.s = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.m = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.g = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.cd = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.mol = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.A = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.magnitude = Integer.parseInt(matcher.group());
  }

  public UnitRepresentation divideBy(UnitRepresentation denominator){
    return new UnitRepresentation(
        this.K -denominator.K,
        this.s -denominator.s,
        this.m - denominator.m,
        this.g - denominator.g,
        this.cd - denominator.cd,
        this.mol -denominator.mol,
        this.A - denominator.A,
        this.magnitude - denominator.magnitude);
  }

  public UnitRepresentation pow(int exponent){
    return new UnitRepresentation(
        this.K * exponent,
        this.s * exponent,
        this.m * exponent,
        this.g * exponent,
        this.cd * exponent,
        this.mol * exponent,
        this.A * exponent,
        this.magnitude* exponent);
  }

  public UnitRepresentation multiplyBy(UnitRepresentation factor){
    return new UnitRepresentation(
        this.K +factor.K,
        this.s +factor.s,
        this.m + factor.m,
        this.g + factor.g,
        this.cd + factor.cd,
        this.mol +factor.mol,
        this.A + factor.A,
        this.magnitude + factor.magnitude);
  }
}