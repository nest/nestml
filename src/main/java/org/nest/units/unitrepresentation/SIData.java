/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;

import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

/**
 * Provides static information about the SI system.
 *
 * @author ptraeder.
 */
public class SIData {

  private static SIData instance=null;
  private UnitRepresentation lumen = UnitRepresentation.getBuilder().cd(1).build();
  private UnitRepresentation siemens = UnitRepresentation.getBuilder().g(-1).m(-2).s(3).A(2).build();
  private UnitRepresentation farad = UnitRepresentation.getBuilder().g(-1).m(-2).s(4).A(2).build();
  private UnitRepresentation joule = UnitRepresentation.getBuilder().g(1).m(2).s(-2).build();
  private UnitRepresentation weber = UnitRepresentation.getBuilder().g(1).m(2).s(-2).A(-1).build();
  private UnitRepresentation henry = UnitRepresentation.getBuilder().g(1).m(2).s(-2).A(-2).build();
  private UnitRepresentation watt = UnitRepresentation.getBuilder().g(1).m(2).s(-3).build();
  private UnitRepresentation volt = UnitRepresentation.getBuilder().g(1).m(2).s(-3).A(-1).build();
  private UnitRepresentation ohm = UnitRepresentation.getBuilder().g(1).m(2).s(-3).A(-2).build();
  private UnitRepresentation pascal = UnitRepresentation.getBuilder().g(1).m(-1).s(-2).build();
  private UnitRepresentation newton = UnitRepresentation.getBuilder().g(1).m(1).s(-2).build();
  private UnitRepresentation tesla = UnitRepresentation.getBuilder().g(1).s(-2).A(-1).build();
  private UnitRepresentation gray = UnitRepresentation.getBuilder().m(2).s(-2).build();
  private UnitRepresentation sievert = UnitRepresentation.getBuilder().m(2).s(-2).build();
  private UnitRepresentation lux = UnitRepresentation.getBuilder().m(-2).cd(1).build();
  private UnitRepresentation hertz = UnitRepresentation.getBuilder().s(-1).build();
  private UnitRepresentation  becquerel = UnitRepresentation.getBuilder().s(-1).build();
  private UnitRepresentation katal = UnitRepresentation.getBuilder().s(-1).mol(1).build();
  private UnitRepresentation coulomb = UnitRepresentation.getBuilder().s(1).A(1).build();

  private UnitRepresentation kelvin = UnitRepresentation.getBuilder().K(1).build();
  private UnitRepresentation second = UnitRepresentation.getBuilder().s(1).build();
  private UnitRepresentation meter = UnitRepresentation.getBuilder().m(1).build();
  //compensate for SI inconsistency with magnitude
  private UnitRepresentation gram = UnitRepresentation.getBuilder().g(1).magnitude(-3).build();
  private UnitRepresentation candela = UnitRepresentation.getBuilder().cd(1).build();
  private UnitRepresentation mole = UnitRepresentation.getBuilder().mol(1).build();
  private UnitRepresentation ampere = UnitRepresentation.getBuilder().A(1).build();

  static private HashMap<String,UnitRepresentation> baseRepresentations = new HashMap();
  static private BiMap<String, Integer> prefixMagnitudes =HashBiMap.create();

  private static ArrayList<String> CorrectSIUnits= new ArrayList<>();
  //ignore dimensionless units radian and steradian. Ignore degree Celsius as Kelvin exists.

  private static String[] SIUnitsRaw =
      {"K","s","m","g","cd","mol","A"};
  private static String[] SIUnitsDerivedRaw =
      {"Hz","N","Pa","J","W","C","V","F","Ohm","S","Wb","T","H","lm","lx","Bq","Gy","Sv","kat"};
  private static String[] SIPrefixesRaw =
      {"da","h","k","M","G","T","P","E","Z","Y","d","c","m","mu","n","p","f","a","z","y"};

  private static List<String> SIUnits = Arrays.asList(SIUnitsRaw);
  private static List<String> SIUnitsDerived = Arrays.asList(SIUnitsDerivedRaw);
  private static List<String> SIPrefixes = Arrays.asList(SIPrefixesRaw);

  private void populateUnitsList(){
    for (String pre: SIPrefixes) {
      for (String unit: SIUnits) {
        CorrectSIUnits.add(pre+unit);
      }
      for (String unit: SIUnitsDerived){
        CorrectSIUnits.add(pre+unit);
      }
    }
    for(String unit:SIUnits){  //also add plain Units
      CorrectSIUnits.add(unit);
    }
    for (String unit: SIUnitsDerived){
      CorrectSIUnits.add(unit);
    }

  }

  /**
   *
   * @return List containing every combination of:
   * <p>-SI prefixes (k,m,mu,n,...)
   * <p>-SI base units (K,s,m,...) and compound units (N,Ohm,V,...)
   */
  public static List<String> getCorrectSIUnits() {
    if(instance == null) {
      instance = new SIData();
    }
    return CorrectSIUnits;
  }

  /**
   *
   * @return List of valid SI prefixes (k,m,mu,n,...)
   */
  public static List<String> getSIPrefixes() {
    return SIPrefixes;
  }

  /**
   *
   * @return Mapping of (derived)SI unit names without prefixes to their internal representation.
   */
  static public HashMap<String,UnitRepresentation> getBaseRepresentations(){
    if(instance == null) {
      instance = new SIData();
    }
    return baseRepresentations;
  }

  /**
   *
   * @return Bidirectional mapping between SI prefixes and the exponent to base 10 they respresent,
   * e.g. k=3,p=-12 etc
   */
  static public BiMap<String, Integer> getPrefixMagnitudes() {
    if(instance == null) {
      instance = new SIData();
    }
    return prefixMagnitudes;
  }

  SIData(){
    populateUnitsList();
    baseRepresentations.put("Hz",hertz);
    baseRepresentations.put("N",newton);
    baseRepresentations.put("Pa",pascal);
    baseRepresentations.put("J",joule);
    baseRepresentations.put("W",watt);
    baseRepresentations.put("C",coulomb);
    baseRepresentations.put("V",volt);
    baseRepresentations.put("F",farad);
    baseRepresentations.put("Ohm",ohm);
    baseRepresentations.put("S",siemens);
    baseRepresentations.put("Wb",weber);
    baseRepresentations.put("T",tesla);
    baseRepresentations.put("H",henry);
    baseRepresentations.put("lm",lumen);
    baseRepresentations.put("lx",lux);
    baseRepresentations.put("Bq",becquerel);
    baseRepresentations.put("Gy",gray);
    baseRepresentations.put("Sv",sievert);
    baseRepresentations.put("kat",katal);

    baseRepresentations.put("K",kelvin);
    baseRepresentations.put("s",second);
    baseRepresentations.put("m",meter);
    baseRepresentations.put("g",gram);
    baseRepresentations.put("cd",candela);
    baseRepresentations.put("mol",mole);
    baseRepresentations.put("A",ampere);

    prefixMagnitudes.put("da",1);
    prefixMagnitudes.put("k",3);
    prefixMagnitudes.put("M",6);
    prefixMagnitudes.put("G",9);
    prefixMagnitudes.put("T",12);
    prefixMagnitudes.put("P",15);
    prefixMagnitudes.put("E",18);
    prefixMagnitudes.put("Z",21);
    prefixMagnitudes.put("Y",24);

    prefixMagnitudes.put("d",-1);
    prefixMagnitudes.put("m",-3);
    prefixMagnitudes.put("mu",-6);
    prefixMagnitudes.put("n",-9);
    prefixMagnitudes.put("p",-12);
    prefixMagnitudes.put("g",-15);
    prefixMagnitudes.put("a",-18);
    prefixMagnitudes.put("z",-21);
    prefixMagnitudes.put("y",-24);
  }

  /**/
}
