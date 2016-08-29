package org.nest.units.unitrepresentation;

import static java.lang.Math.abs;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.google.common.base.Preconditions;
import javafx.util.Pair;

/**
 * @author ptraeder
 * Helper class. Controlled way of creating base representations of derived SI units.
 */

public class UnitRepresentation {
  private int magnitude;
  private int K,s,m,g,cd,mol,A;

  private int[] asArray(){
    int[] result={ K, s, m, g, cd, mol, A, magnitude };
    return result;
  }

  public void addMagnitude(int magnitude) {
    this.magnitude += magnitude;
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

  private boolean isZero(){
    return (this.exponentSum() == 0) ? true : false;
  }

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
        //At this point we know that both modulo of both (nonzero) components is 0
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

  private String divideIntoParts(){
    String bestMatch = "";
    UnitRepresentation smallestRemainder = this;
    for (String unitName : SIData.getBaseRepresentations().keySet()){
      if(! unitName.equals("Hz") && !unitName.equals("Bq")) { //Explicitly exclude synonyms for 1/s
        //Try Pow
        UnitRepresentation baseUnit = SIData.getBaseRepresentations().get(unitName);
        Optional<Integer> pow = getExponent(baseUnit);
        if(pow.isPresent()){
          UnitRepresentation thisRemainder = this.divideBy(baseUnit.pow(pow.get()));

          if (smallestRemainder.isMoreComplexThan(thisRemainder)) {
            bestMatch = unitName + "**"+pow.get()+" * ";
            smallestRemainder = thisRemainder;
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
          bestMatch = unitName +"**-1 * " ;
          smallestRemainder = thisRemainder;
        }
      }
    }
    if(bestMatch.equals("")) { //abort recursion
      return smallestRemainder.isZero() ? "" : smallestRemainder.naivePrint();
    }

    return bestMatch + smallestRemainder.divideIntoParts();
  }

  private String naivePrint(){
    String numerator =
        (K==1? "K * " : K>0? "(K**"+K+") * " :"")
            + (s==1? "s * " : s>0? "(s**"+s+") * " :"")
            + (m==1? "m * " : m>0? "(m**"+m+") * " :"")
            + (g==1? "g * " : g>0? "(g**"+g+") * " :"")
            + (cd==1? "cd * " : cd>0? "(cd**"+cd+") * " :"")
            + (mol==1? "mol * " : mol>0? "(mol**"+mol+") * " :"")
            + (A==1? "A * " : A>0? "(A**"+A+") * " :"");
    if(numerator.length() > 0 ){
      numerator = numerator.substring(0,numerator.length()-3);
      if(numerator.contains("*")){
        numerator = "("+numerator+")";
      }
    }else{
      numerator ="1";
    }
    String denominator =
        (K==-1? "K * " : K<0? "(K**"+-K+") * " :"")
            + (s==-1? "s * " : s<0? "(s**"+-s+") * " :"")
            + (m==-1? "m * " : m<0? "(m**"+-m+") * " :"")
            + (g==-1? "g * " : g<0? "(g**"+-g+") * " :"")
            + (cd==-1? "cd * " : cd<0? "(cd**"+-cd+") * " :"")
            + (mol==-1? "mol * " : mol<0? "(mol**"+-mol+") * " :"")
            + (A==-1? "A * " : A<0? "(A**"+-A+") * " :"");
    if(denominator.length()>1){
      denominator = denominator.substring(0,denominator.length()- 3);
      if(denominator.contains("*")){
        denominator = "("+denominator+")";
      }
    }else{
      denominator ="";
    }
    return (magnitude!=0? "e"+magnitude+"*":"")+ numerator + (denominator.length()>0? " / "+denominator : "");
  }

  public String prettyPrint() {
    String result = this.divideIntoParts();
    String postfix = result.substring(result.length()-3,result.length());
    if(postfix.equals(" * ")){
      return result.substring(0,result.length()-3);
    }else{
      return result;
    }
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
    }
    if(SIData.getBaseRepresentations().containsKey(unit)) { //No prefix present, see if whole name matches
      UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(unit));
      return Optional.of(result);
    }
    try{
      UnitRepresentation unitRepresentation = new UnitRepresentation(unit);
      return Optional.of(unitRepresentation);
    }catch(Exception e){}
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

  public UnitRepresentation invert(){
    return new UnitRepresentation(-K,-s,-m,-g,-cd,-mol,-A,-magnitude);
  }
}