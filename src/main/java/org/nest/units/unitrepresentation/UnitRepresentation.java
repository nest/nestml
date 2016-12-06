/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;

import com.google.common.base.Preconditions;
import javafx.util.Pair;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static java.lang.Math.abs;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * Helper class. Controlled way of creating base representations of derived SI units.
 *
 * @author plotnikov, traeder
 */
public class UnitRepresentation implements Comparable<UnitRepresentation>{
  private final String ERROR_CODE = "NESTML_UnitRepresentation: ";

  public void setMagnitude(int magnitude) {
    this.magnitude = magnitude;
  }

  private int magnitude;
  private int K, s, m, g, cd, mol, A;

  private boolean ignoreMagnitude = false;

  public void setIgnoreMagnitude(boolean ignoreMagnitude) {
    this.ignoreMagnitude = ignoreMagnitude;
  }

  public boolean isIgnoreMagnitude() {
    return ignoreMagnitude;
  }


  private int[] asArray(){
    int[] result={ K, s, m, g, cd, mol, A, magnitude };
    return result;
  }

  private void increaseMagnitude(int difference) {
    this.magnitude += difference;
  }

  public String serialize() {
    return Arrays.toString(this.asArray())+(ignoreMagnitude?"I":"i");
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

  public int compareTo(UnitRepresentation other) {
    if(this.isMoreComplexThan(other)){
      return 1;
    }else if(other.isMoreComplexThan(this)){
      return -1;
    }
    return 0;
  }

  /**
   * Helper class for organizing printing
   */

  class Factor {
    public void setName(String name) {
      this.name = name;
    }

    private  String name;
    private  int exponent;

    public Factor(String name, int exponent){
      this.name = name;
      this.exponent = exponent;
    }

    public String getName() {
      return name;
    }

    public int getExponent() {
      return exponent;
    }
  }


  private String calculateName() {
    //
    //copy this because side effects.
    UnitRepresentation workingCopy = new UnitRepresentation(this);

    //factorize
    List<Factor> factors = new ArrayList<>();
    if(!factorize(factors,workingCopy)){
      error(ERROR_CODE+ "Cannot factorize the Unit "+workingCopy.serialize());
      return("unprintable");
    }

    //dump magnitude back into the results
    if(abs(this.magnitude)>factors.size()*24){
      warn(ERROR_CODE+ "Cannot express magnitude "+magnitude+" with only " +(factors.size())+ "factors. (Absolute value of) cumulative magnitude must be <=24.");
      return("unprintable");
    }
    dumpMagnitude(factors,this.magnitude);

    //print resulting factorization
    return printresults(factors);
  }

  private void dumpMagnitude(List<Factor> factors, int magnitude) {
    int thisDump,nextDump;
    if(abs(magnitude)>24){
      if(magnitude<0){
        thisDump = -24;
        nextDump = magnitude+24;
      }else{
        thisDump = 24;
        nextDump = magnitude-24;
      }
    }else{
      thisDump=magnitude;
      nextDump = 0;
    }

    Factor first = factors.remove(0);
    String firstName = first.getName();
    String prefix = "";
    if(thisDump !=0) {
      prefix = SIData.getPrefixMagnitudes().inverse().get(thisDump);
    }
    first.setName(prefix+firstName);

    if(nextDump!=0){
      dumpMagnitude(factors,nextDump);
    }

    List<Factor> restoreFactors= new ArrayList<>(); //juggle values around to retain order or matches
    restoreFactors.add(first);
    restoreFactors.addAll(factors);
    factors.removeAll(factors);
    factors.addAll(restoreFactors);
  }

  private String printresults(List<Factor> factors) {
    String numerator ="",denominator="";
    int numCount=0,denomCount=0;
    for(Factor factor : factors){
      if(factor.getExponent() >0){
        numCount++;
        numerator += factor.getName() + (factor.getExponent()>1 ? "**" + factor.getExponent() : "" ) + " * ";
      }else{
        denomCount++;
        denominator += factor.getName()+(factor.getExponent()<-1 ? "**" + -factor.getExponent() : "" )+" * ";
      }
    }

    if(numerator ==""){
      numerator = "1";
    }


    numerator = removeTrailingMultiplication(numerator);
    if(numCount>1){
      numerator = "("+numerator+")";
    }

    denominator = removeTrailingMultiplication(denominator);
    if(denomCount>1){
      denominator="("+denominator+")";
    }

    return numerator+(denomCount>0?  " / "+ denominator:"");
  }

  private class FactorizationResult implements Comparable<FactorizationResult>{
    private UnitRepresentation remainder;
    private Factor factor;

    public FactorizationResult(UnitRepresentation remainder, Factor factor){
      this.remainder = remainder;
      this.factor = factor;
    }

    @Override public int compareTo(FactorizationResult o) {
      if(this.remainder.compareTo(o.remainder)==0){
        String tieBreakerThis = this.factor.getName()+this.factor.getExponent(); //Make sure that TreeSet actually gets to add stuff
        String tieBreakerOther = o.factor.getName()+o.factor.getExponent();
        return tieBreakerThis.compareTo(tieBreakerOther);
      }
      return this.remainder.compareTo(o.remainder);
    }
  }

  private boolean factorize(List<Factor> factors, UnitRepresentation workingCopy) {
    /* Find the highest possible power of any given BaseRepresentation to still be contained in workingCopy.
     */
    Set<FactorizationResult> orderedResults = new TreeSet<FactorizationResult>();
    for(String baseName : SIData.getBaseRepresentations().keySet()){
      if(baseName.equals("Bq")|| baseName.equals("Hz")||    //skip matching Bq and Hz in favour of 1/s
          baseName.equals("S")){                            //skip matching S in favour of 1/Ohm
        continue;
      }

      UnitRepresentation base = SIData.getBaseRepresentations().get(baseName);
      //match base in workingCopy
      Pair<Integer,UnitRepresentation> match = workingCopy.match(base);
      UnitRepresentation remainder = match.getValue();
      Factor factor = new Factor(baseName,match.getKey());
      orderedResults.add(new FactorizationResult(remainder,factor));
      //match for inverse base
      match = workingCopy.match(base.invert());
      UnitRepresentation inverseRemainder = match.getValue();
      Factor inverseFactor = new Factor(baseName,-match.getKey());
      orderedResults.add(new FactorizationResult(inverseRemainder,inverseFactor));
    }

    if(orderedResults.isEmpty()){
      return false;
    }

    for(FactorizationResult result : orderedResults){
      if(result.remainder.exponentSum() == 0){
        factors.add(result.factor);
        return true;
      }
      List<Factor> nextResults = new ArrayList<>();
      if(factorize(nextResults,result.remainder)){ //remaining factorization successful?
        factors.add(result.factor);//construct result in factors parameter
        factors.addAll(nextResults);
        return true;
      }
    }
    return false;
  }

  private Pair<Integer, UnitRepresentation> match(UnitRepresentation base) {
    if(this.contains(base)){ //base is factor with positive exponent
      int exponent = 1;
      while(this.contains(base.pow(++exponent))){} //step up until we lose match
      exponent--; //step back once
      return new Pair(exponent,this.divideBy(base.pow(exponent)));

    }else{ //base is not a factor: return division result anyways so we can expand if nothing else matches
      return new Pair(1,this.divideBy(base));
    }
  }

  private boolean contains(UnitRepresentation base) {
    int expSumPre = this.exponentSum()+abs(this.magnitude);
    UnitRepresentation division = this.divideBy(base);
    int expSumPost = division.exponentSum()+abs(division.magnitude);
    if(expSumPre - expSumPost == (base.exponentSum()+abs(base.magnitude))){
      return true;
    }else {
      return false;
    }
  }

  public String prettyPrint() {
    if(isZero()){
      return "real";
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
    try{      UnitRepresentation unitRepresentation = new UnitRepresentation(unit);
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
    this.ignoreMagnitude = false;
  }

  public UnitRepresentation(int K, int s, int m, int g, int cd, int mol, int A, int magnitude,boolean ignoreMagnitude) {
    this.K = K;
    this.s = s;
    this.m = m;
    this.g = g;
    this.cd = cd;
    this.mol = mol;
    this.A = A;
    this.magnitude = magnitude;
    this.ignoreMagnitude = ignoreMagnitude;
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
    this.ignoreMagnitude= unit.isIgnoreMagnitude();
  }

  public boolean equals(UnitRepresentation other){
    //ignore magnitude if either is set to ignore.
    if(this.isIgnoreMagnitude()||other.isIgnoreMagnitude()){
      return (this.K == other.K &&
          this.s == other.s &&
          this.m == other.m &&
          this.g == other.g &&
          this.cd == other.cd &&
          this.mol == other.mol &&
          this.A == other.A);
    }else {
      return (this.K == other.K &&
          this.s == other.s &&
          this.m == other.m &&
          this.g == other.g &&
          this.cd == other.cd &&
          this.mol == other.mol &&
          this.A == other.A &&
          this.magnitude == other.magnitude);
    }
  }


  public UnitRepresentation(String serialized){
    if(serialized == getRealType().getName()) {
      return; //[0,0,0,0,0,0,0,0]i
    }

    if(serialized.substring(serialized.length()-1).equals("I")){
      ignoreMagnitude = true;
    }

    Pattern parse = Pattern.compile("-?[0-9]+");
    Matcher matcher = parse.matcher(serialized);

    checkState(matcher.find());
    this.K = Integer.parseInt(matcher.group());
    checkState(matcher.find());
    this.s = Integer.parseInt(matcher.group());
    checkState(matcher.find());
    this.m = Integer.parseInt(matcher.group());
    checkState(matcher.find());
    this.g = Integer.parseInt(matcher.group());
    checkState(matcher.find());
    this.cd = Integer.parseInt(matcher.group());
    checkState(matcher.find());
    this.mol = Integer.parseInt(matcher.group());
    checkState(matcher.find());
    this.A = Integer.parseInt(matcher.group());
    checkState(matcher.find());
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
        this.magnitude - denominator.magnitude,
        this.isIgnoreMagnitude()||denominator.isIgnoreMagnitude());
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
        this.magnitude* exponent,
        this.isIgnoreMagnitude());
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
        this.magnitude + factor.magnitude,
        this.isIgnoreMagnitude()||factor.isIgnoreMagnitude());
  }

  public UnitRepresentation invert(){
    return new UnitRepresentation(-K,-s,-m,-g,-cd,-mol,-A,-magnitude,this.isIgnoreMagnitude());
  }

  public UnitRepresentation deriveT(int order) {
    UnitRepresentation result = new UnitRepresentation(this);
    result.s -= order;
    return result;
  }
}