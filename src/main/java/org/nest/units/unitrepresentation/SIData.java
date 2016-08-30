/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.units.unitrepresentation;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;

/**
 * provides access to commonly used SI data.
 *
 * @author ptraeder.
 */
public class SIData {

  private static SIData instance=null;
  private UnitRepresentation lumen = new UnitRepresentation(0,0,0,0,1,0,0,0);
  private UnitRepresentation siemens = new UnitRepresentation(0,3,-2,-1,0,0,2,0);
  private UnitRepresentation farad = new UnitRepresentation(0,4,-2,-1,0,0,2,0);
  private UnitRepresentation joule = new UnitRepresentation(0,-2,2,1,0,0,0,0);
  private UnitRepresentation weber = new UnitRepresentation(0,-2,2,1,0,0,-1,0);
  private UnitRepresentation henry = new UnitRepresentation(0,-2,2,1,0,0,-2,0);
  private UnitRepresentation watt = new UnitRepresentation(0,-3,2,1,0,0,0,0);
  private UnitRepresentation volt = new UnitRepresentation(0,-3,2,1,0,0,-1,0);
  private UnitRepresentation ohm = new UnitRepresentation(0,-3,2,1,0,0,-2,0);
  private UnitRepresentation pascal = new UnitRepresentation(0,-2,-1,1,0,0,0,0);
  private UnitRepresentation newton = new UnitRepresentation(0,-2,1,1,0,0,0,0);
  private UnitRepresentation tesla = new UnitRepresentation(0,-2,1,0,0,0,-1,0);
  private UnitRepresentation gray = new UnitRepresentation(0,-2,2,0,0,0,0,0);
  private UnitRepresentation sievert = new UnitRepresentation(0,-2,2,0,0,0,0,0);
  private UnitRepresentation lux = new UnitRepresentation(0,0,-2,0,1,0,0,0);
  private UnitRepresentation hertz = new UnitRepresentation(0,-1,0,0,0,0,0,0);
  private UnitRepresentation  becquerel = new UnitRepresentation(0,-1,0,0,0,0,0,0);
  private UnitRepresentation katal = new UnitRepresentation(0,-1,0,0,0,1,0,0);
  private UnitRepresentation coulomb = new UnitRepresentation(0,1,0,0,0,0,1,0);

  private UnitRepresentation kelvin = new UnitRepresentation(1,0,0,0,0,0,0,0);
  private UnitRepresentation second = new UnitRepresentation(0,1,0,0,0,0,0,0);
  private UnitRepresentation meter = new UnitRepresentation(0,0,1,0,0,0,0,0);
  //compensate for SI inconsistency with magnitude
  private UnitRepresentation gram = new UnitRepresentation(0,0,0,1,0,0,0,-3);
  private UnitRepresentation candela = new UnitRepresentation(0,0,0,0,1,0,0,0);
  private UnitRepresentation mole = new UnitRepresentation(0,0,0,0,0,1,0,0);
  private UnitRepresentation ampere = new UnitRepresentation(0,0,0,0,0,0,1,0);

  static private HashMap<String,UnitRepresentation> baseRepresentations = new HashMap();
  static private BiMap<String, Integer> prefixMagnitudes =HashBiMap.create();

  private static ArrayList<String> CorrectSIUnits= new ArrayList<>();
  //ignore dimensionless units radian and steradian. Ignore degree Celsius as Kelvin exists.

  private static String[] SIUnitsRaw ={"K","s","m","g","cd","mol","A"};
  private static String[] SIUnitsDerivedRaw = {"Hz","N","Pa","J","W","C","V","F","Ohm","S","Wb","T","H","lm","lx","Bq","Gy","Sv","kat"};
  private static String[] SIPrefixesRaw ={"da","h","k","M","G","T","P","E","Z","Y","d","c","m","mu","n","p","f","a","z","y"};

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

  public static ArrayList<String> getCorrectSIUnits() {
    if(instance == null) {
      instance = new SIData();
    }
    return CorrectSIUnits;
  }

  public static List<String> getSIPrefixes() {
    return SIPrefixes;
  }

  public static List<String> getSIUnitsDerived() {
    return SIUnitsDerived;
  }

  public static List<String> getSIUnits() {
    return SIUnits;
  }

  static public HashMap<String,UnitRepresentation> getBaseRepresentations(){
    if(instance == null) {
      instance = new SIData();
    }
    return baseRepresentations;
  }

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
    prefixMagnitudes.put("h",2);
    prefixMagnitudes.put("k",3);
    prefixMagnitudes.put("M",6);
    prefixMagnitudes.put("G",9);
    prefixMagnitudes.put("T",12);
    prefixMagnitudes.put("P",15);
    prefixMagnitudes.put("E",18);
    prefixMagnitudes.put("Z",21);
    prefixMagnitudes.put("Y",24);

    prefixMagnitudes.put("d",-1);
    prefixMagnitudes.put("c",-2);
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
