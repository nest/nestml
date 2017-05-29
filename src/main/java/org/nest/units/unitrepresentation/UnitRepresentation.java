/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;

import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.units._cocos.UnitsErrorStrings;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.trace;
import static de.se_rwth.commons.logging.Log.warn;
import static java.lang.Math.abs;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * Internal representation of SI Units. Supplies arithmetic functions on units and
 * (de)serializes them.
 *
 * @author plotnikov, traeder
 */
public class UnitRepresentation implements Comparable<UnitRepresentation>{

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

  /**
   * Helper class, used in printing to maintain possible factorizations for backtracking purposes.
   */
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

  /**
   * Builder for UnitRepresentations.
   */
  public static class Builder{
    private int magnitude;
    private int K, s, m, g, cd, mol, A;
    private boolean ignoreMagnitude = false;
    private boolean errorState = false;
    private String serialization;
    private String unitName;

    /**
     *
     * @param K exponent to temperature
     */
    public Builder K(int K){
      this.K = K;
      return this;
    }
    /**
     *
     * @param s exponent to time
     */
    public Builder s(int s){
      this.s = s;
      return this;
    }

    /**
     *
     * @param m exponent to distance
     */
    public Builder m(int m){
      this.m = m;
      return this;
    }

    /**
     *
     * @param g exponent to mass
     */
    public Builder g(int g){
      this.g = g;
      return this;
    }

    /**
     *
     * @param cd exponent to luminous intensity
     */
    public Builder cd(int cd){
      this.cd = cd;
      return this;
    }

    /**
     *
     * @param mol exponent to amount of substance
     */
    public Builder mol(int mol){
      this.mol = mol;
      return this;
    }

    /**
     *
     * @param A exponent to current
     */
    public Builder A(int A){
      this.A = A;
      return this;
    }

    /**
     *
     * @param magnitude scaling factor. Exponent to base 10.
     */
    public Builder magnitude(int magnitude){
      this.magnitude = magnitude;
      return this;
    }

    /**
     *
     * @param ignoreMagnitude set ignoreMagnitude for the resulting UnitRepresentation
     */
    public Builder ignoreMagnitude(boolean ignoreMagnitude) {
      this.ignoreMagnitude = ignoreMagnitude;
      return this;
    }

    /**
     * Attempts to parse a UnitRepresentation from a serialization.
     * Throws IllegalStateException if errors are encountered.
     * Used predominantly to reconstruct a UnitRepresentation from a TypeSymbol name for further handling.
     *
     * @param serialization serialized UnitRepresentation.
     */
    public Builder serialization(String serialization){
      if(serialization == getRealType().getName()) {
        return this; //[0,0,0,0,0,0,0,0]i
      }

      if(serialization.substring(serialization.length()-1).equals("I")){
        this.ignoreMagnitude = true;
      }

      Pattern parse = Pattern.compile("-?[0-9]+");
      Matcher matcher = parse.matcher(serialization);

      if(matcher.find()) {
        this.K = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.s = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.m = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.g = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.cd = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.mol = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.A = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      if(matcher.find()) {
        this.magnitude = Integer.parseInt(matcher.group());
      } else{
        this.errorState = true;
      }
      checkState(!errorState,
          "NESTML_UnitRepresentation: Cannot parse unitRepresentation from the string '"+serialization+"'");

      return this;
    }

    /**
     * This builder option replaces a copy constructor.
     * @param other Unit to copy.
     */
    public Builder other(UnitRepresentation other){
      this.K = other.K;
      this.s = other.s;
      this.m = other.m;
      this.g = other.g;
      this.cd = other.cd;
      this.mol = other.mol;
      this.A = other.A;
      this.magnitude = other.magnitude;
      this.ignoreMagnitude= other.isIgnoreMagnitude();
      return this;
    }

    /**
     *
     * @return The UnitRepresentation built from provided data.
     */
    public UnitRepresentation build(){
      return new UnitRepresentation(K,s,m,g,cd,mol,A,magnitude,ignoreMagnitude);
    }
  }

  private int magnitude;
  private int K, s, m, g, cd, mol, A;
  private boolean ignoreMagnitude = false;
  private static UnitFilter targetUnitFilter = new NESTMLUnitFilter();

  public static UnitFilter getTargetUnitFilter(){
    return targetUnitFilter;
  }

  public int getMagnitude() {
    return magnitude;
  }

  /**
   *
   * @return Builder Object for construction of UnitRepresentations
   */
  public static Builder getBuilder(){
    return new Builder();
  }

  /**
   *
   * @param ignoreMagnitude new value for ignoreMagnitude
   */
  public void setIgnoreMagnitude(boolean ignoreMagnitude) {
    this.ignoreMagnitude = ignoreMagnitude;
  }

  /**
   *
   * @return the current value of ingoreMagnitude
   */
  public boolean isIgnoreMagnitude() {
    return ignoreMagnitude;
  }

  /**
   * Serializes the unit.
   *
   * @return Serialized array of the units' SI related fields (= "[K,s,m,g,cd,mol,A,magnitude]")
   * extended by either a lowercase i if ignoreMagnitude is not set, or an uppercase I if it is.
   * E.g. kN without ignoreMagnitude would be serialized as "[0,-2,1,1,0,0,0,3]i"
   */
  public String serialize() {
    return Arrays.toString(this.asArray())+(ignoreMagnitude?"I":"i");
  }

  /**
   *
   * @return returns true iff the sum of absolute values of SI fields + magnitude is zero
   */
  public boolean isZero(){
    return (this.exponentSum()+abs(this.magnitude) == 0) ? true : false;
  }

  /**
   *
   * @param other The unit to compare this to
   * @return 1 if the sum of absolutes of this units' SI fields (excluding magnitude) is greater than other's
   * <p> -1 if the sum of absolutes of this units' SI fields (excluding magnitude) is smaller than other's
   * <p> 0 if both sums are equal.
   */
  public int compareTo(UnitRepresentation other) {
    if(this.isMoreComplexThan(other)){
      return 1;
    }else if(other.isMoreComplexThan(this)){
      return -1;
    }
    return 0;
  }

  /**
   *
   * @return A copy of the object with magnitude set to 0
   */
  public UnitRepresentation getBase(){
    UnitRepresentation result = getBuilder().other(this).magnitude(0).build();
    return result;
  }
  /**
   *
   * @return A valid name for the given Unit. Not guaranteed to match the declaration of the type, but at least equivalent.
   */
  public String prettyPrint() {
    if(isZero()){
      return "real";
    }
    return  calculateName();
  }

  /**
   *
   * @param unit Name of an SI unit including prefix, e.g. kN, pA, MV,...
   * @return UnitRepresentation equivalent to unit given as parameter, if existent.
   */
  static public Optional<UnitRepresentation> lookupName(String unit){
    for (String pre: SIData.getSIPrefixes()){
      if(pre.regionMatches(false,0,unit,0,pre.length())){
        //See if remaining unit name matches a valid SI Unit. Since some prefixes are not unique
        String remainder = unit.substring(pre.length());
        if(SIData.getBaseRepresentations().containsKey(remainder)){
          int magnitude = SIData.getPrefixMagnitudes().get(pre);
          UnitRepresentation result = getBuilder().other(SIData.getBaseRepresentations().get(remainder)).build();
          result.increaseMagnitude(magnitude);
          return Optional.of(result);
        }

      }

    }
    if(SIData.getBaseRepresentations().containsKey(unit)) { //No prefix present, see if whole name matches
      UnitRepresentation result = getBuilder().other(SIData.getBaseRepresentations().get(unit)).build();
      return Optional.of(result);
    }
    return Optional.empty();
  }

  /**
   * Comparison of <b>this</b> with <b>other</b>
   * <p>If either <b>this</b> or <b>other</b> has the ignoreMagnitude bit set, magnitudes are ignored.
   *
   * @param other the unit to compare <b>this</b> to.
   * @return if both UnitRepresentations have ignoreMagnitude set: true iff all fields match.
   * <p> otherwise: true iff all fields but magnitude match.
   *
   */
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
    UnitRepresentation result = getBuilder().other(this).build();
    UnitRepresentation denominator = getBuilder().s(order).magnitude(-3*order).build();
    result = result.divideBy(denominator);
    return result;
  }

  private UnitRepresentation(int K, int s, int m, int g, int cd, int mol, int A, int magnitude,boolean ignoreMagnitude) {
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

  private void increaseMagnitude(int difference) {
    this.magnitude += difference;
  }

  private int exponentSum() {
    return abs(K)+abs(s)+abs(m)+abs(g)+abs(cd)+abs(mol)+abs(A);
  }

  private int[] asArray(){
    int[] result={ K, s, m, g, cd, mol, A, magnitude };
    return result;
  }

  private boolean isMoreComplexThan(UnitRepresentation other){
    return (this.exponentSum() > other.exponentSum()) ? true : false;
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
    //
    //copy this because side effects.
    UnitRepresentation workingCopy = getBuilder().other(this).build();

    //factorize
    List<Factor> factors = new ArrayList<>();
    if(!factorize(factors,workingCopy)){
      error(UnitsErrorStrings.code(this) + ": Cannot factorize the Unit "+workingCopy.serialize());
      return "unprintable";
    }

    //dump magnitude back into the results
    if(abs(this.magnitude)>factors.size()*24){
      trace(UnitsErrorStrings.code(this) + "Cannot express magnitude " + magnitude + " with only " + (factors.size()) +
            " factors. (Absolute value of) cumulative magnitude must be <=24.", this.getClass().getSimpleName());
      return "unprintable";
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
      int toDump =0; //dump modified by exponent to current factor
      if(thisDump%first.getExponent() != 0){
        toDump = ((thisDump/first.getExponent())/3)*3;
        nextDump += (thisDump-toDump*first.getExponent());
      }else {
        toDump = thisDump/first.getExponent();
      }
      prefix = SIData.getPrefixMagnitudes().inverse().get(toDump);
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

  private boolean factorize(List<Factor> factors, UnitRepresentation workingCopy) {
    /* Find the highest possible power of any given BaseRepresentation to still be contained in workingCopy.
     */
    Set<FactorizationResult> orderedResults = new TreeSet<>();
    for(String baseName : SIData.getBaseRepresentations().keySet()){
      if(baseName.equals("Bq")|| baseName.equals("Hz")||    //skip matching Bq and Hz in favour of 1/s
          baseName.equals("S")){                            //skip matching S in favour of 1/Ohm
        continue;
      }

      UnitRepresentation base = SIData.getBaseRepresentations().get(baseName);
      //match base in workingCopy
      Map.Entry<Integer,UnitRepresentation> match = workingCopy.match(base);
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

  private Map.Entry<Integer,UnitRepresentation> match(UnitRepresentation base) {
    if(this.contains(base)){ //base is factor with positive exponent
      int exponent = 1;
      while(this.contains(base.pow(++exponent))){} //step up until we lose match
      exponent--; //step back once
      return new AbstractMap.SimpleEntry<>(exponent,this.divideBy(base.pow(exponent)));

    }else{ //base is not a factor: return division result anyways so we can expand if nothing else matches
      return new AbstractMap.SimpleEntry<>(1,this.divideBy(base));
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


}