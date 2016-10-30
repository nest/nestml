/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;

import com.google.common.base.Preconditions;
import de.se_rwth.commons.logging.Log;

import java.util.Arrays;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static de.se_rwth.commons.logging.Log.warn;
import static java.lang.Math.abs;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;

/**
 * Helper class. Controlled way of creating base representations of derived SI units.
 *
 * @author plotnikov, traeder
 */
public class UnitRepresentation {
  private static final String LOG_NAME = "NESTML_UNIT_REPRESENTATION";
  private int magnitude;
  private int K, s, m, g, cd, mol, A;

  private int[] asArray(){
    int[] result={ K, s, m, g, cd, mol, A, magnitude };
    return result;
  }

  private void increaseMagnitude(int difference) {
    this.magnitude += difference;
  }

  public String serialize() {
    return Arrays.toString(this.asArray());
  }

  private int exponentSum() {
    return abs(K)+abs(s)+abs(m)+abs(g)+abs(cd)+abs(mol)+abs(A);
  }

  private boolean isMoreComplexThan(UnitRepresentation other){
    return (this.exponentSum() > other.exponentSum()) ? true : false;
  }

  public boolean isZero(){
    return (this.exponentSum()+abs(this.magnitude) == 0) ? true : false;
  }

  /** calculates, if existent, the power of the base unit that this represents.
   * I.e. calculates x in:
   *
   *    base**x = this
   *
   *    iff x is a integer
   *
   *
   * TODO: rewrite to not require exact matching for a more intuitive overall match
   * i.e. account for:
   *    this = base**x * y
   *
   *    where x is an integer and y is a unit type.
   */
  private Optional<Integer> getExponent(UnitRepresentation base){
    int[] thisUnits = this.asArray();
    int[] baseUnits = base.asArray();
    Integer factor = null;
    for (int i=0;i<thisUnits.length;i++){
      int thisValue = thisUnits[i];
      int baseValue = baseUnits[i];
      if(thisValue ==0 && baseValue != 0 ||
          thisValue !=0 && baseValue == 0) {
        return Optional.empty();
      }
      if(thisValue !=0){
        if(thisValue % baseValue != 0) {
          return Optional.empty();
        }
        //At this point we know that modulo of both (nonzero) components is 0
        if(factor == null) {
          factor = thisValue / baseValue;
        }
        else if(factor != thisValue/baseValue){
          return Optional.empty();
        }
      }
    }

    if(factor != null)
      return Optional.of(factor);
    else
      return Optional.empty();
  }

  private String doCalc(){
    String bestMatch = "";
    UnitRepresentation smallestRemainder = this;
    for (String unitName : SIData.getBaseRepresentations().keySet()){
      if(! unitName.equals("Hz") && !unitName.equals("Bq")) { //Explicitly exclude synonyms for 1/s
        //Try Pow
        UnitRepresentation baseUnit = SIData.getBaseRepresentations().get(unitName);
        Optional<Integer> pow = getExponent(baseUnit);
        if(pow.isPresent()){
          int exponent = pow.get();
          UnitRepresentation thisRemainder = this.divideBy(baseUnit.pow(exponent));

          if (smallestRemainder.isMoreComplexThan(thisRemainder)) {
            if(!(unitName == "S" && exponent == -1) &&//Avoid S**-1 in favor of Ohm
                !(unitName == "Ohm" && exponent == -1)){ //Avoid Ohm**-1 in favor of S
              bestMatch = unitName + (exponent != 1 ? "**"+pow.get()+" * ": " * ");
              smallestRemainder = thisRemainder;
            }
          }
        }


        //Try Division by Base Units
        UnitRepresentation thisRemainder = this.divideBy(baseUnit);
        if (smallestRemainder.isMoreComplexThan(thisRemainder)) {
          bestMatch = unitName + " * ";
          smallestRemainder = thisRemainder;
        }

        //Try Inverse base Units:
        thisRemainder = this.divideBy(baseUnit.invert());
        if(smallestRemainder.isMoreComplexThan(thisRemainder)){
          if(unitName != "S" &&//Avoid S**-1 in favor of Ohm
              unitName != "Ohm") { //Avoid Ohm**-1 in favor of S
            bestMatch = unitName + "**-1 * ";
            smallestRemainder = thisRemainder;
          }
        }
      }
    }
    if(bestMatch.equals("")) { //abort recursion
      return smallestRemainder.isZero() ? "" : smallestRemainder.defaultPrint();
    }
    return bestMatch + smallestRemainder.doCalc();

  }

  private String removeTrailingMultiplication(String str){
    if(str.length() <3){
      return str;
    }
    String result = str;
    String postfix = result.substring(result.length() - 3, result.length());
    if (postfix.equals(" * ")) {
      result = result.substring(0, result.length() - 3);
    }
    return result;
  }


  private String calculateName() {
    String result = this.doCalc();
    result = removeTrailingMultiplication(result);
    int exponentIndex = result.indexOf("e");
    if(exponentIndex != -1){ // Exponential notation present
      String[] parts = result.split("e");
      if(parts.length == 2){
        String main = parts[0];
        String magnitude = parts[1];
        main = removeTrailingMultiplication(main);

        result ="";
        String lastUnit="";

        if(main.contains(" * ")){  //There is more than one Unit in the calculated name -> Isolate the last one.
          String[] mainParts = main.split(" \\* ");
          for(int i = 0; i<mainParts.length-1; i++){
            result += mainParts[i] + " * ";
          }
          lastUnit = mainParts[mainParts.length-1];
        }else{
          lastUnit = main;
        }

        try {
          Integer parsedMagnitude = Integer.parseInt(magnitude);
          if(lastUnit.contains("**-")) { //The single/last  unit has a negative exponent
            parsedMagnitude = -parsedMagnitude;
          }
          String prefix = SIData.getPrefixMagnitudes().inverse().get(parsedMagnitude);
          return result+prefix+lastUnit;
        }
        catch(NumberFormatException e){
          warn("Exception in Unit name Formatting! Cannot parse magnitude String: "
              +magnitude);
          return result;
        }
      }
    }
    return result;
  }

  private String defaultPrint(){
    String result =
        (K==1? "K * " : K!=0? "K**"+K+" * " :"")
            + (s==1? "s * " : s!=0? "s**"+s+" * " :"")
            + (m==1? "m * " : m!=0? "m**"+m+" * " :"")
            + (g==1? "g * " : g!=0? "g**"+g+" * " :"")
            + (cd==1? "cd * " : cd!=0? "cd**"+cd+" * " :"")
            + (mol==1? "mol * " : mol!=0? "mol**"+mol+" * " :"")
            + (A==1? "A * " : A!=0? "A**"+A+" * " :"");
    if(result.length() > 0 ){
      result = result.substring(0,result.length()-3);
    }

    return result + (magnitude!=0? "e"+magnitude:"");
  }

  public String prettyPrint() {
    if(isZero()){
      return "no dimension";
    }
    return  calculateName();
  }

  static public Optional<UnitRepresentation> lookupName(String unit){
    for (String pre: SIData.getSIPrefixes()){
      if(pre.regionMatches(false,0,unit,0,pre.length())){
        //See if remaining unit name matches a valid SI Unit. Since some prefixes are not unique
        String remainder = unit.substring(pre.length());
        if(SIData.getBaseRepresentations().containsKey(remainder)){
          int magnitude = SIData.getPrefixMagnitudes().get(pre);
          UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(remainder));
          result.increaseMagnitude(magnitude);
          return Optional.of(result);
        }

      }

    }
    if(SIData.getBaseRepresentations().containsKey(unit)) { //No prefix present, see if whole name matches
      UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(unit));
      return Optional.of(result);
    }
    try{
      UnitRepresentation unitRepresentation = new UnitRepresentation(unit);
      return Optional.of(unitRepresentation);
    }
    catch(Exception e){
      //should never happen
      return Optional.empty();
    }

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

  public boolean equals(UnitRepresentation other){
    if(this.K == other.K &&
        this.s == other.s &&
        this.m == other.m &&
        this.g == other.g &&
        this.cd == other.cd &&
        this.mol == other.mol &&
        this.A == other.A &&
        this.magnitude == other.magnitude){
      return true;
    }else{
      return false;
    }
  }

  public UnitRepresentation(String serialized){
    if(serialized == getRealType().getName()) {
      return; //[0,0,0,0,0,0,0,0]
    }

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

  public UnitRepresentation invert(){
    return new UnitRepresentation(-K,-s,-m,-g,-cd,-mol,-A,-magnitude);
  }

  public UnitRepresentation deriveT(int order) {
    UnitRepresentation result = new UnitRepresentation(this);
    result.s -= order;
    return result;
  }
}