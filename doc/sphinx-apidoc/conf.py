# -*- coding: utf-8 -*-
#
# conf.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""
Readthedocs configuration file
------------------------------

Use:
sphinx-build -c ../extras/help_generator -b html . _build/html

"""

import sys
import os


import pip

# pip.main(['install', 'Sphinx==1.5.6'])
# pip.main(['install', 'sphinx-gallery'])

# import sphinx_gallery
import subprocess

# import shlex

from subprocess import check_output, CalledProcessError
from pygments.lexer import RegexLexer, include, bygroups, using, this, inherit, default, combined, words
from pygments import token
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Punctuation, Error
from sphinx.highlighting import lexers

class NESTMLLexer(RegexLexer):
    
    """Based on the Pygments PythonLexer"""
    
    name = "NESTML"
    filenames = ['*.nestml']

    def innerstring_rules(ttype):
        return [
            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'\n', Text),
            (r'[^\S\n]+', Text),
            (r'#.*$', Comment.Single),
            (r'//.*$', Comment.Single),
            (r'[]{}:(),;[]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            include('keywords'),
            include('builtins'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(""")',
             bygroups(String.Affix, String.Double), 'tdqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(''')",
             bygroups(String.Affix, String.Single), 'tsqs'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            ('([uUbB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            ("([uUbB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            include('name'),
            include('numbers'),
        ],
        'keywords': [
            (words((
                "recordable", 		"shape", 		"neuron", 		"state", 		"parameters", 		"internals", 		"initial_values", 		"update", 		"equations", 		"input", 		"output", 		"current", 		"spike", "inhibitory", "excitatory", "end", "function", "return", "if", "elif", "else", "for", "while", "in", "step", "and", "or", "not"), suffix=r'\b'),
             Keyword),
        ],
        'types': [
            (words(("integer", 	"real", 	"string", 	"boolean", 	"void", 	"A", 	"AA", 	"Angstrom", 	"Bq", 	"C", 	"Celsius", 	"Ci", 	"EA", 	"EC", 	"EF", 	"EH", 	"EHz", 	"EJ", 	"EK", 	"EL", 	"EN", 	"EOhm", 	"EPa", 	"ES", 	"ET", 	"EV", 	"EW", 	"EWb", 	"Ea", 	"Earcmin", 	"Earcsec", 	"Ecd", 	"Ed", 	"Edeg", 	"EeV", 	"Eg", 	"Eh", 	"El", 	"Elm", 	"Elx", 	"Em", 	"Emin", 	"Emol", 	"Eohm", 	"Erad", 	"Es", 	"Esr", 	"Eyr", 	"F", 	"Farad", 	"GA", 	"GC", 	"GF", 	"GH", 	"GHz", 	"GJ", 	"GK", 	"GL", 	"GN", 	"GOhm", 	"GPa", 	"GS", 	"GT", 	"GV", 	"GW", 	"GWb", 	"Ga", 	"Garcmin", 	"Garcsec", 	"Gcd", 	"Gd", 	"Gdeg", 	"GeV", 	"Gg", 	"Gh", 	"Gl", 	"Glm", 	"Glx", 	"Gm", 	"Gmin", 	"Gmol", 	"Gohm", 	"Grad", 	"Gs", 	"Gsr", 	"Gyr", 	"H", 	"Henry", 	"Hertz", 	"Hz", 	"J", 	"Joule", 	"K", 	"Kelvin", 	"L", 	"MA", 	"MC", 	"MF", 	"MH", 	"MHz", 	"MJ", 	"MK", 	"ML", 	"MN", 	"MOhm", 	"MPa", 	"MS", 	"MT", 	"MV", 	"MW", 	"MWb", 	"Ma", 	"Marcmin", 	"Marcsec", 	"Mcd", 	"Md", 	"Mdeg", 	"MeV", 	"Mg", 	"Mh", 	"Ml", 	"Mlm", 	"Mlx", 	"Mm", 	"Mmin", 	"Mmol", 	"Mohm", 	"Mrad", 	"Ms", 	"Msr", 	"Myr", 	"N", 	"Newton", 	"Ohm", 	"PA", 	"PC", 	"PF", 	"PH", 	"PHz", 	"PJ", 	"PK", 	"PL", 	"PN", 	"POhm", 	"PPa", 	"PS", 	"PT", 	"PV", 	"PW", 	"PWb", 	"Pa", 	"Parcmin", 	"Parcsec", 	"Pascal", 	"Pcd", 	"Pd", 	"Pdeg", 	"PeV", 	"Pg", 	"Ph", 	"Pl", 	"Plm", 	"Plx", 	"Pm", 	"Pmin", 	"Pmol", 	"Pohm", 	"Prad", 	"Ps", 	"Psr", 	"Pyr", 	"S", 	"Siemens", 	"T", 	"TA", 	"TC", 	"TF", 	"TH", 	"THz", 	"TJ", 	"TK", 	"TL", 	"TN", 	"TOhm", 	"TPa", 	"TS", 	"TT", 	"TV", 	"TW", 	"TWb", 	"Ta", 	"Tarcmin", 	"Tarcsec", 	"Tcd", 	"Td", 	"Tdeg", 	"TeV", 	"Tesla", 	"Tg", 	"Th", 	"Tl", 	"Tlm", 	"Tlx", 	"Tm", 	"Tmin", 	"Tmol", 	"Tohm", 	"Trad", 	"Ts", 	"Tsr", 	"Tyr", 	"V", 	"Volt", 	"W", 	"Watt", 	"Wb", 	"Weber", 	"YA", 	"YC", 	"YF", 	"YH", 	"YHz", 	"YJ", 	"YK", 	"YL", 	"YN", 	"YOhm", 	"YPa", 	"YS", 	"YT", 	"YV", 	"YW", 	"YWb", 	"Ya", 	"Yarcmin", 	"Yarcsec", 	"Ycd", 	"Yd", 	"Ydeg", 	"YeV", 	"Yg", 	"Yh", 	"Yl", 	"Ylm", 	"Ylx", 	"Ym", 	"Ymin", 	"Ymol", 	"Yohm", 	"Yrad", 	"Ys", 	"Ysr", 	"Yyr", 	"ZA", 	"ZC", 	"ZF", 	"ZH", 	"ZHz", 	"ZJ", 	"ZK", 	"ZL", 	"ZN", 	"ZOhm", 	"ZPa", 	"ZS", 	"ZT", 	"ZV", 	"ZW", 	"ZWb", 	"Za", 	"Zarcmin", 	"Zarcsec", 	"Zcd", 	"Zd", 	"Zdeg", 	"ZeV", 	"Zg", 	"Zh", 	"Zl", 	"Zlm", 	"Zlx", 	"Zm", 	"Zmin", 	"Zmol", 	"Zohm", 	"Zrad", 	"Zs", 	"Zsr", 	"Zyr", 	"a", 	"aA", 	"aC", 	"aF", 	"aH", 	"aHz", 	"aJ", 	"aK", 	"aL", 	"aN", 	"aOhm", 	"aPa", 	"aS", 	"aT", 	"aV", 	"aW", 	"aWb", 	"aa", 	"aarcmin", 	"aarcsec", 	"acd", 	"ad", 	"adeg", 	"aeV", 	"ag", 	"ah", 	"al", 	"alm", 	"alx", 	"am", 	"amin", 	"amol", 	"amp", 	"ampere", 	"angstrom", 	"annum", 	"aohm", 	"arad", 	"arcmin", 	"arcminute", 	"arcsec", 	"arcsecond", 	"asr", 	"attoFarad", 	"attoHenry", 	"attoHertz", 	"attoJoule", 	"attoKelvin", 	"attoNewton", 	"attoOhm", 	"attoPascal", 	"attoSiemens", 	"attoTesla", 	"attoVolt", 	"attoWatt", 	"attoWeber", 	"attoamp", 	"attoampere", 	"attoannum", 	"attoarcminute", 	"attoarcsecond", 	"attocandela", 	"attocoulomb", 	"attoday", 	"attodegree", 	"attoelectronvolt", 	"attofarad", 	"attogram", 	"attohenry", 	"attohertz", 	"attohour", 	"attohr", 	"attojoule", 	"attoliter", 	"attolumen", 	"attolux", 	"attometer", 	"attominute", 	"attomole", 	"attonewton", 	"attopascal", 	"attoradian", 	"attosecond", 	"attosiemens", 	"attosteradian", 	"attotesla", 	"attovolt", 	"attowatt", 	"attoweber", 	"attoyear", 	"ayr", 	"bar", 	"bases", 	"becquerel", 	"cA", 	"cC", 	"cF", 	"cH", 	"cHz", 	"cJ", 	"cK", 	"cL", 	"cN", 	"cOhm", 	"cPa", 	"cS", 	"cT", 	"cV", 	"cW", 	"cWb", 	"ca", 	"candela", 	"carcmin", 	"carcsec", 	"ccd", 	"cd", 	"cdeg", 	"ceV", 	"centiFarad", 	"centiHenry", 	"centiHertz", 	"centiJoule", 	"centiKelvin", 	"centiNewton", 	"centiOhm", 	"centiPascal", 	"centiSiemens", 	"centiTesla", 	"centiVolt", 	"centiWatt", 	"centiWeber", 	"centiamp", 	"centiampere", 	"centiannum", 	"centiarcminute", 	"centiarcsecond", 	"centicandela", 	"centicoulomb", 	"centiday", 	"centidegree", 	"centielectronvolt", 	"centifarad", 	"centigram", 	"centihenry", 	"centihertz", 	"centihour", 	"centihr", 	"centijoule", 	"centiliter", 	"centilumen", 	"centilux", 	"centimeter", 	"centiminute", 	"centimole", 	"centinewton", 	"centipascal", 	"centiradian", 	"centisecond", 	"centisiemens", 	"centisteradian", 	"centitesla", 	"centivolt", 	"centiwatt", 	"centiweber", 	"centiyear", 	"cg", 	"ch", 	"cl", 	"clm", 	"clx", 	"cm", 	"cmin", 	"cmol", 	"cohm", 	"coulomb", 	"crad", 	"cs", 	"csr", 	"curie", 	"cyr", 	"d", 	"dA", 	"dC", 	"dF", 	"dH", 	"dHz", 	"dJ", 	"dK", 	"dL", 	"dN", 	"dOhm", 	"dPa", 	"dS", 	"dT", 	"dV", 	"dW", 	"dWb", 	"da", 	"daA", 	"daC", 	"daF", 	"daH", 	"daHz", 	"daJ", 	"daK", 	"daL", 	"daN", 	"daOhm", 	"daPa", 	"daS", 	"daT", 	"daV", 	"daW", 	"daWb", 	"daa", 	"daarcmin", 	"daarcsec", 	"dacd", 	"dad", 	"dadeg", 	"daeV", 	"dag", 	"dah", 	"dal", 	"dalm", 	"dalx", 	"dam", 	"damin", 	"damol", 	"daohm", 	"darad", 	"darcmin", 	"darcsec", 	"das", 	"dasr", 	"day", 	"dayr", 	"dcd", 	"dd", 	"ddeg", 	"deV", 	"decaFarad", 	"decaHenry", 	"decaHertz", 	"decaJoule", 	"decaKelvin", 	"decaNewton", 	"decaOhm", 	"decaPascal", 	"decaSiemens", 	"decaTesla", 	"decaVolt", 	"decaWatt", 	"decaWeber", 	"decaamp", 	"decaampere", 	"decaannum", 	"decaarcminute", 	"decaarcsecond", 	"decacandela", 	"decacoulomb", 	"decaday", 	"decadegree", 	"decaelectronvolt", 	"decafarad", 	"decagram", 	"decahenry", 	"decahertz", 	"decahour", 	"decahr", 	"decajoule", 	"decaliter", 	"decalumen", 	"decalux", 	"decameter", 	"decaminute", 	"decamole", 	"decanewton", 	"decapascal", 	"decaradian", 	"decasecond", 	"decasiemens", 	"decasteradian", 	"decatesla", 	"decavolt", 	"decawatt", 	"decaweber", 	"decayear", 	"deciFarad", 	"deciHenry", 	"deciHertz", 	"deciJoule", 	"deciKelvin", 	"deciNewton", 	"deciOhm", 	"deciPascal", 	"deciSiemens", 	"deciTesla", 	"deciVolt", 	"deciWatt", 	"deciWeber", 	"deciamp", 	"deciampere", 	"deciannum", 	"deciarcminute", 	"deciarcsecond", 	"decicandela", 	"decicoulomb", 	"deciday", 	"decidegree", 	"decielectronvolt", 	"decifarad", 	"decigram", 	"decihenry", 	"decihertz", 	"decihour", 	"decihr", 	"decijoule", 	"deciliter", 	"decilumen", 	"decilux", 	"decimeter", 	"deciminute", 	"decimole", 	"decinewton", 	"decipascal", 	"deciradian", 	"decisecond", 	"decisiemens", 	"decisteradian", 	"decitesla", 	"decivolt", 	"deciwatt", 	"deciweber", 	"deciyear", 	"deg", 	"deg_C", 	"degree", 	"dekaFarad", 	"dekaHenry", 	"dekaHertz", 	"dekaJoule", 	"dekaKelvin", 	"dekaNewton", 	"dekaOhm", 	"dekaPascal", 	"dekaSiemens", 	"dekaTesla", 	"dekaVolt", 	"dekaWatt", 	"dekaWeber", 	"dekaamp", 	"dekaampere", 	"dekaannum", 	"dekaarcminute", 	"dekaarcsecond", 	"dekacandela", 	"dekacoulomb", 	"dekaday", 	"dekadegree", 	"dekaelectronvolt", 	"dekafarad", 	"dekagram", 	"dekahenry", 	"dekahertz", 	"dekahour", 	"dekahr", 	"dekajoule", 	"dekaliter", 	"dekalumen", 	"dekalux", 	"dekameter", 	"dekaminute", 	"dekamole", 	"dekanewton", 	"dekapascal", 	"dekaradian", 	"dekasecond", 	"dekasiemens", 	"dekasteradian", 	"dekatesla", 	"dekavolt", 	"dekawatt", 	"dekaweber", 	"dekayear", 	"dg", 	"dh", 	"division", 	"dl", 	"dlm", 	"dlx", 	"dm", 	"dmin", 	"dmol", 	"dohm", 	"drad", 	"ds", 	"dsr", 	"dyr", 	"eV", 	"electronvolt", 	"exaFarad", 	"exaHenry", 	"exaHertz", 	"exaJoule", 	"exaKelvin", 	"exaNewton", 	"exaOhm", 	"exaPascal", 	"exaSiemens", 	"exaTesla", 	"exaVolt", 	"exaWatt", 	"exaWeber", 	"exaamp", 	"exaampere", 	"exaannum", 	"exaarcminute", 	"exaarcsecond", 	"exacandela", 	"exacoulomb", 	"exaday", 	"exadegree", 	"exaelectronvolt", 	"exafarad", 	"exagram", 	"exahenry", 	"exahertz", 	"exahour", 	"exahr", 	"exajoule", 	"exaliter", 	"exalumen", 	"exalux", 	"exameter", 	"examinute", 	"examole", 	"exanewton", 	"exapascal", 	"exaradian", 	"exasecond", 	"exasiemens", 	"exasteradian", 	"exatesla", 	"exavolt", 	"exawatt", 	"exaweber", 	"exayear", 	"fA", 	"fC", 	"fF", 	"fH", 	"fHz", 	"fJ", 	"fK", 	"fL", 	"fN", 	"fOhm", 	"fPa", 	"fS", 	"fT", 	"fV", 	"fW", 	"fWb", 	"fa", 	"farad", 	"farcmin", 	"farcsec", 	"fcd", 	"fd", 	"fdeg", 	"feV", 	"femtoFarad", 	"femtoHenry", 	"femtoHertz", 	"femtoJoule", 	"femtoKelvin", 	"femtoNewton", 	"femtoOhm", 	"femtoPascal", 	"femtoSiemens", 	"femtoTesla", 	"femtoVolt", 	"femtoWatt", 	"femtoWeber", 	"femtoamp", 	"femtoampere", 	"femtoannum", 	"femtoarcminute", 	"femtoarcsecond", 	"femtocandela", 	"femtocoulomb", 	"femtoday", 	"femtodegree", 	"femtoelectronvolt", 	"femtofarad", 	"femtogram", 	"femtohenry", 	"femtohertz", 	"femtohour", 	"femtohr", 	"femtojoule", 	"femtoliter", 	"femtolumen", 	"femtolux", 	"femtometer", 	"femtominute", 	"femtomole", 	"femtonewton", 	"femtopascal", 	"femtoradian", 	"femtosecond", 	"femtosiemens", 	"femtosteradian", 	"femtotesla", 	"femtovolt", 	"femtowatt", 	"femtoweber", 	"femtoyear", 	"fg", 	"fh", 	"fl", 	"flm", 	"flx", 	"fm", 	"fmin", 	"fmol", 	"fohm", 	"fortnight", 	"frad", 	"fs", 	"fsr", 	"fyr", 	"g", 	"gigaFarad", 	"gigaHenry", 	"gigaHertz", 	"gigaJoule", 	"gigaKelvin", 	"gigaNewton", 	"gigaOhm", 	"gigaPascal", 	"gigaSiemens", 	"gigaTesla", 	"gigaVolt", 	"gigaWatt", 	"gigaWeber", 	"gigaamp", 	"gigaampere", 	"gigaannum", 	"gigaarcminute", 	"gigaarcsecond", 	"gigacandela", 	"gigacoulomb", 	"gigaday", 	"gigadegree", 	"gigaelectronvolt", 	"gigafarad", 	"gigagram", 	"gigahenry", 	"gigahertz", 	"gigahour", 	"gigahr", 	"gigajoule", 	"gigaliter", 	"gigalumen", 	"gigalux", 	"gigameter", 	"gigaminute", 	"gigamole", 	"giganewton", 	"gigapascal", 	"gigaradian", 	"gigasecond", 	"gigasiemens", 	"gigasteradian", 	"gigatesla", 	"gigavolt", 	"gigawatt", 	"gigaweber", 	"gigayear", 	"gram", 	"h", 	"hA", 	"hC", 	"hF", 	"hH", 	"hHz", 	"hJ", 	"hK", 	"hL", 	"hN", 	"hOhm", 	"hPa", 	"hS", 	"hT", 	"hV", 	"hW", 	"hWb", 	"ha", 	"harcmin", 	"harcsec", 	"hcd", 	"hd", 	"hdeg", 	"heV", 	"hectoFarad", 	"hectoHenry", 	"hectoHertz", 	"hectoJoule", 	"hectoKelvin", 	"hectoNewton", 	"hectoOhm", 	"hectoPascal", 	"hectoSiemens", 	"hectoTesla", 	"hectoVolt", 	"hectoWatt", 	"hectoWeber", 	"hectoamp", 	"hectoampere", 	"hectoannum", 	"hectoarcminute", 	"hectoarcsecond", 	"hectocandela", 	"hectocoulomb", 	"hectoday", 	"hectodegree", 	"hectoelectronvolt", 	"hectofarad", 	"hectogram", 	"hectohenry", 	"hectohertz", 	"hectohour", 	"hectohr", 	"hectojoule", 	"hectoliter", 	"hectolumen", 	"hectolux", 	"hectometer", 	"hectominute", 	"hectomole", 	"hectonewton", 	"hectopascal", 	"hectoradian", 	"hectosecond", 	"hectosiemens", 	"hectosteradian", 	"hectotesla", 	"hectovolt", 	"hectowatt", 	"hectoweber", 	"hectoyear", 	"henry", 	"hertz", 	"hg", 	"hh", 	"hl", 	"hlm", 	"hlx", 	"hm", 	"hmin", 	"hmol", 	"hohm", 	"hour", 	"hourangle", 	"hr", 	"hrad", 	"hs", 	"hsr", 	"hyr", 	"joule", 	"kA", 	"kC", 	"kF", 	"kH", 	"kHz", 	"kJ", 	"kK", 	"kL", 	"kN", 	"kOhm", 	"kPa", 	"kS", 	"kT", 	"kV", 	"kW", 	"kWb", 	"ka", 	"karcmin", 	"karcsec", 	"kcd", 	"kd", 	"kdeg", 	"keV", 	"kg", 	"kh", 	"kiloFarad", 	"kiloHenry", 	"kiloHertz", 	"kiloJoule", 	"kiloKelvin", 	"kiloNewton", 	"kiloOhm", 	"kiloPascal", 	"kiloSiemens", 	"kiloTesla", 	"kiloVolt", 	"kiloWatt", 	"kiloWeber", 	"kiloamp", 	"kiloampere", 	"kiloannum", 	"kiloarcminute", 	"kiloarcsecond", 	"kilocandela", 	"kilocoulomb", 	"kiloday", 	"kilodegree", 	"kiloelectronvolt", 	"kilofarad", 	"kilogram", 	"kilohenry", 	"kilohertz", 	"kilohour", 	"kilohr", 	"kilojoule", 	"kiloliter", 	"kilolumen", 	"kilolux", 	"kilometer", 	"kilominute", 	"kilomole", 	"kilonewton", 	"kilopascal", 	"kiloradian", 	"kilosecond", 	"kilosiemens", 	"kilosteradian", 	"kilotesla", 	"kilovolt", 	"kilowatt", 	"kiloweber", 	"kiloyear", 	"kl", 	"klm", 	"klx", 	"km", 	"kmin", 	"kmol", 	"kohm", 	"krad", 	"ks", 	"ksr", 	"kyr", 	"l", 	"liter", 	"lm", 	"lumen", 	"lux", 	"lx", 	"m", 	"mA", 	"mC", 	"mF", 	"mH", 	"mHz", 	"mJ", 	"mK", 	"mL", 	"mN", 	"mOhm", 	"mPa", 	"mS", 	"mT", 	"mV", 	"mW", 	"mWb", 	"ma", 	"marcmin", 	"marcsec", 	"mas", 	"mcd", 	"md", 	"mdeg", 	"meV", 	"megaFarad", 	"megaHenry", 	"megaHertz", 	"megaJoule", 	"megaKelvin", 	"megaNewton", 	"megaOhm", 	"megaPascal", 	"megaSiemens", 	"megaTesla", 	"megaVolt", 	"megaWatt", 	"megaWeber", 	"megaamp", 	"megaampere", 	"megaannum", 	"megaarcminute", 	"megaarcsecond", 	"megacandela", 	"megacoulomb", 	"megaday", 	"megadegree", 	"megaelectronvolt", 	"megafarad", 	"megagram", 	"megahenry", 	"megahertz", 	"megahour", 	"megahr", 	"megajoule", 	"megaliter", 	"megalumen", 	"megalux", 	"megameter", 	"megaminute", 	"megamole", 	"meganewton", 	"megapascal", 	"megaradian", 	"megasecond", 	"megasiemens", 	"megasteradian", 	"megatesla", 	"megavolt", 	"megawatt", 	"megaweber", 	"megayear", 	"meter", 	"mg", 	"mh", 	"microFarad", 	"microHenry", 	"microHertz", 	"microJoule", 	"microKelvin", 	"microNewton", 	"microOhm", 	"microPascal", 	"microSiemens", 	"microTesla", 	"microVolt", 	"microWatt", 	"microWeber", 	"microamp", 	"microampere", 	"microannum", 	"microarcminute", 	"microarcsecond", 	"microcandela", 	"microcoulomb", 	"microday", 	"microdegree", 	"microelectronvolt", 	"microfarad", 	"microgram", 	"microhenry", 	"microhertz", 	"microhour", 	"microhr", 	"microjoule", 	"microliter", 	"microlumen", 	"microlux", 	"micrometer", 	"microminute", 	"micromole", 	"micron", 	"micronewton", 	"micropascal", 	"microradian", 	"microsecond", 	"microsiemens", 	"microsteradian", 	"microtesla", 	"microvolt", 	"microwatt", 	"microweber", 	"microyear", 	"milliFarad", 	"milliHenry", 	"milliHertz", 	"milliJoule", 	"milliKelvin", 	"milliNewton", 	"milliOhm", 	"milliPascal", 	"milliSiemens", 	"milliTesla", 	"milliVolt", 	"milliWatt", 	"milliWeber", 	"milliamp", 	"milliampere", 	"milliannum", 	"milliarcminute", 	"milliarcsecond", 	"millicandela", 	"millicoulomb", 	"milliday", 	"millidegree", 	"millielectronvolt", 	"millifarad", 	"milligram", 	"millihenry", 	"millihertz", 	"millihour", 	"millihr", 	"millijoule", 	"milliliter", 	"millilumen", 	"millilux", 	"millimeter", 	"milliminute", 	"millimole", 	"millinewton", 	"millipascal", 	"milliradian", 	"millisecond", 	"millisiemens", 	"millisteradian", 	"millitesla", 	"millivolt", 	"milliwatt", 	"milliweber", 	"milliyear", 	"min", 	"minute", 	"ml", 	"mlm", 	"mlx", 	"mm", 	"mmin", 	"mmol", 	"mohm", 	"mol", 	"mole", 	"mrad", 	"ms", 	"msr", 	"myr", 	"nA", 	"nC", 	"nF", 	"nH", 	"nHz", 	"nJ", 	"nK", 	"nL", 	"nN", 	"nOhm", 	"nPa", 	"nS", 	"nT", 	"nV", 	"nW", 	"nWb", 	"na", 	"nanoFarad", 	"nanoHenry", 	"nanoHertz", 	"nanoJoule", 	"nanoKelvin", 	"nanoNewton", 	"nanoOhm", 	"nanoPascal", 	"nanoSiemens", 	"nanoTesla", 	"nanoVolt", 	"nanoWatt", 	"nanoWeber", 	"nanoamp", 	"nanoampere", 	"nanoannum", 	"nanoarcminute", 	"nanoarcsecond", 	"nanocandela", 	"nanocoulomb", 	"nanoday", 	"nanodegree", 	"nanoelectronvolt", 	"nanofarad", 	"nanogram", 	"nanohenry", 	"nanohertz", 	"nanohour", 	"nanohr", 	"nanojoule", 	"nanoliter", 	"nanolumen", 	"nanolux", 	"nanometer", 	"nanominute", 	"nanomole", 	"nanonewton", 	"nanopascal", 	"nanoradian", 	"nanosecond", 	"nanosiemens", 	"nanosteradian", 	"nanotesla", 	"nanovolt", 	"nanowatt", 	"nanoweber", 	"nanoyear", 	"narcmin", 	"narcsec", 	"ncd", 	"nd", 	"ndeg", 	"neV", 	"newton", 	"ng", 	"nh", 	"nl", 	"nlm", 	"nlx", 	"nm", 	"nmin", 	"nmol", 	"nohm", 	"nrad", 	"ns", 	"nsr", 	"nyr", 	"ohm", 	"pA", 	"pC", 	"pF", 	"pH", 	"pHz", 	"pJ", 	"pK", 	"pL", 	"pN", 	"pOhm", 	"pPa", 	"pS", 	"pT", 	"pV", 	"pW", 	"pWb", 	"pa", 	"parcmin", 	"parcsec", 	"pascal", 	"pcd", 	"pct", 	"pd", 	"pdeg", 	"peV", 	"percent", 	"petaFarad", 	"petaHenry", 	"petaHertz", 	"petaJoule", 	"petaKelvin", 	"petaNewton", 	"petaOhm", 	"petaPascal", 	"petaSiemens", 	"petaTesla", 	"petaVolt", 	"petaWatt", 	"petaWeber", 	"petaamp", 	"petaampere", 	"petaannum", 	"petaarcminute", 	"petaarcsecond", 	"petacandela", 	"petacoulomb", 	"petaday", 	"petadegree", 	"petaelectronvolt", 	"petafarad", 	"petagram", 	"petahenry", 	"petahertz", 	"petahour", 	"petahr", 	"petajoule", 	"petaliter", 	"petalumen", 	"petalux", 	"petameter", 	"petaminute", 	"petamole", 	"petanewton", 	"petapascal", 	"petaradian", 	"petasecond", 	"petasiemens", 	"petasteradian", 	"petatesla", 	"petavolt", 	"petawatt", 	"petaweber", 	"petayear", 	"pg", 	"picoFarad", 	"picoHenry", 	"picoHertz", 	"picoJoule", 	"picoKelvin", 	"picoNewton", 	"picoOhm", 	"picoPascal", 	"picoSiemens", 	"picoTesla", 	"picoVolt", 	"picoWatt", 	"picoWeber", 	"picoamp", 	"picoampere", 	"picoannum", 	"picoarcminute", 	"picoarcsecond", 	"picocandela", 	"picocoulomb", 	"picoday", 	"picodegree", 	"picoelectronvolt", 	"picofarad", 	"picogram", 	"picohenry", 	"picohertz", 	"picohour", 	"picohr", 	"picojoule", 	"picoliter", 	"picolumen", 	"picolux", 	"picometer", 	"picominute", 	"picomole", 	"piconewton", 	"picopascal", 	"picoradian", 	"picosecond", 	"picosiemens", 	"picosteradian", 	"picotesla", 	"picovolt", 	"picowatt", 	"picoweber", 	"picoyear", 	"pl", 	"plm", 	"plx", 	"pm", 	"pmin", 	"pmol", 	"pohm", 	"prad", 	"ps", 	"psr", 	"pyr", 	"rad", 	"radian", 	"s", 	"sday", 	"second", 	"siemens", 	"sr", 	"steradian", 	"t", 	"teraFarad", 	"teraHenry", 	"teraHertz", 	"teraJoule", 	"teraKelvin", 	"teraNewton", 	"teraOhm", 	"teraPascal", 	"teraSiemens", 	"teraTesla", 	"teraVolt", 	"teraWatt", 	"teraWeber", 	"teraamp", 	"teraampere", 	"teraannum", 	"teraarcminute", 	"teraarcsecond", 	"teracandela", 	"teracoulomb", 	"teraday", 	"teradegree", 	"teraelectronvolt", 	"terafarad", 	"teragram", 	"terahenry", 	"terahertz", 	"terahour", 	"terahr", 	"terajoule", 	"teraliter", 	"teralumen", 	"teralux", 	"terameter", 	"teraminute", 	"teramole", 	"teranewton", 	"terapascal", 	"teraradian", 	"terasecond", 	"terasiemens", 	"terasteradian", 	"teratesla", 	"teravolt", 	"terawatt", 	"teraweber", 	"terayear", 	"tesla", 	"tonne", 	"uA", 	"uC", 	"uF", 	"uH", 	"uHz", 	"uJ", 	"uK", 	"uL", 	"uN", 	"uOhm", 	"uPa", 	"uS", 	"uT", 	"uV", 	"uW", 	"uWb", 	"ua", 	"uarcmin", 	"uarcsec", 	"uas", 	"ucd", 	"ud", 	"udeg", 	"ueV", 	"ug", 	"uh", 	"ul", 	"ulm", 	"ulx", 	"um", 	"umin", 	"umol", 	"uohm", 	"urad", 	"us", 	"usr", 	"uyr", 	"volt", 	"watt", 	"weber", 	"week", 	"wk", 	"yA", 	"yC", 	"yF", 	"yH", 	"yHz", 	"yJ", 	"yK", 	"yL", 	"yN", 	"yOhm", 	"yPa", 	"yS", 	"yT", 	"yV", 	"yW", 	"yWb", 	"ya", 	"yarcmin", 	"yarcsec", 	"ycd", 	"ydeg", 	"yeV", 	"year", 	"yg", 	"yh", 	"yl", 	"ylm", 	"ylx", 	"ym", 	"ymin", 	"ymol", 	"yoctoFarad", 	"yoctoHenry", 	"yoctoHertz", 	"yoctoJoule", 	"yoctoKelvin", 	"yoctoNewton", 	"yoctoOhm", 	"yoctoPascal", 	"yoctoSiemens", 	"yoctoTesla", 	"yoctoVolt", 	"yoctoWatt", 	"yoctoWeber", 	"yoctoamp", 	"yoctoampere", 	"yoctoannum", 	"yoctoarcminute", 	"yoctoarcsecond", 	"yoctocandela", 	"yoctocoulomb", 	"yoctoday", 	"yoctodegree", 	"yoctoelectronvolt", 	"yoctofarad", 	"yoctogram", 	"yoctohenry", 	"yoctohertz", 	"yoctohour", 	"yoctohr", 	"yoctojoule", 	"yoctoliter", 	"yoctolumen", 	"yoctolux", 	"yoctometer", 	"yoctominute", 	"yoctomole", 	"yoctonewton", 	"yoctopascal", 	"yoctoradian", 	"yoctosecond", 	"yoctosiemens", 	"yoctosteradian", 	"yoctotesla", 	"yoctovolt", 	"yoctowatt", 	"yoctoweber", 	"yoctoyear", 	"yohm", 	"yottaFarad", 	"yottaHenry", 	"yottaHertz", 	"yottaJoule", 	"yottaKelvin", 	"yottaNewton", 	"yottaOhm", 	"yottaPascal", 	"yottaSiemens", 	"yottaTesla", 	"yottaVolt", 	"yottaWatt", 	"yottaWeber", 	"yottaamp", 	"yottaampere", 	"yottaannum", 	"yottaarcminute", 	"yottaarcsecond", 	"yottacandela", 	"yottacoulomb", 	"yottaday", 	"yottadegree", 	"yottaelectronvolt", 	"yottafarad", 	"yottagram", 	"yottahenry", 	"yottahertz", 	"yottahour", 	"yottahr", 	"yottajoule", 	"yottaliter", 	"yottalumen", 	"yottalux", 	"yottameter", 	"yottaminute", 	"yottamole", 	"yottanewton", 	"yottapascal", 	"yottaradian", 	"yottasecond", 	"yottasiemens", 	"yottasteradian", 	"yottatesla", 	"yottavolt", 	"yottawatt", 	"yottaweber", 	"yottayear", 	"yr", 	"yrad", 	"ys", 	"ysr", 	"yyr", 	"zA", 	"zC", 	"zF", 	"zH", 	"zHz", 	"zJ", 	"zK", 	"zL", 	"zN", 	"zOhm", 	"zPa", 	"zS", 	"zT", 	"zV", 	"zW", 	"zWb", 	"za", 	"zarcmin", 	"zarcsec", 	"zcd", 	"zd", 	"zdeg", 	"zeV", 	"zeptoFarad", 	"zeptoHenry", 	"zeptoHertz", 	"zeptoJoule", 	"zeptoKelvin", 	"zeptoNewton", 	"zeptoOhm", 	"zeptoPascal", 	"zeptoSiemens", 	"zeptoTesla", 	"zeptoVolt", 	"zeptoWatt", 	"zeptoWeber", 	"zeptoamp", 	"zeptoampere", 	"zeptoannum", 	"zeptoarcminute", 	"zeptoarcsecond", 	"zeptocandela", 	"zeptocoulomb", 	"zeptoday", 	"zeptodegree", 	"zeptoelectronvolt", 	"zeptofarad", 	"zeptogram", 	"zeptohenry", 	"zeptohertz", 	"zeptohour", 	"zeptohr", 	"zeptojoule", 	"zeptoliter", 	"zeptolumen", 	"zeptolux", 	"zeptometer", 	"zeptominute", 	"zeptomole", 	"zeptonewton", 	"zeptopascal", 	"zeptoradian", 	"zeptosecond", 	"zeptosiemens", 	"zeptosteradian", 	"zeptotesla", 	"zeptovolt", 	"zeptowatt", 	"zeptoweber", 	"zeptoyear", 	"zettaFarad", 	"zettaHenry", 	"zettaHertz", 	"zettaJoule", 	"zettaKelvin", 	"zettaNewton", 	"zettaOhm", 	"zettaPascal", 	"zettaSiemens", 	"zettaTesla", 	"zettaVolt", 	"zettaWatt", 	"zettaWeber", 	"zettaamp", 	"zettaampere", 	"zettaannum", 	"zettaarcminute", 	"zettaarcsecond", 	"zettacandela", 	"zettacoulomb", 	"zettaday", 	"zettadegree", 	"zettaelectronvolt", 	"zettafarad", 	"zettagram", 	"zettahenry", 	"zettahertz", 	"zettahour", 	"zettahr", 	"zettajoule", 	"zettaliter", 	"zettalumen", 	"zettalux", 	"zettameter", 	"zettaminute", 	"zettamole", 	"zettanewton", 	"zettapascal", 	"zettaradian", 	"zettasecond", 	"zettasiemens", 	"zettasteradian", 	"zettatesla", 	"zettavolt", 	"zettawatt", 	"zettaweber", 	"zettayear", 	"zg", 	"zh", 	"zl", 	"zlm", 	"zlx", 	"zm", 	"zmin", 	"zmol", 	"zohm", 	"zrad", 	"zs", 	"zsr", 	"zyr", 	"Ba", 	"Barye", 	"Bi", 	"Biot", 	"C", 	"D", 	"Debye", 	"EBa", 	"ED", 	"EG", 	"EGal", 	"EP", 	"ESt", 	"Edyn", 	"Eerg", 	"Ek", 	"Fr", 	"Franklin", 	"G", 	"GBa", 	"GD", 	"GG", 	"GGal", 	"GP", 	"GSt", 	"Gal", 	"Gauss", 	"Gdyn", 	"Gerg", 	"Gk", 	"K", 	"Kayser", 	"MBa", 	"MD", 	"MG", 	"MGal", 	"MP", 	"MSt", 	"Mdyn", 	"Merg", 	"Mk", 	"P", 	"PBa", 	"PD", 	"PG", 	"PGal", 	"PP", 	"PSt", 	"Pdyn", 	"Perg", 	"Pk", 	"St", 	"TBa", 	"TD", 	"TG", 	"TGal", 	"TP", 	"TSt", 	"Tdyn", 	"Terg", 	"Tk", 	"YBa", 	"YD", 	"YG", 	"YGal", 	"YP", 	"YSt", 	"Ydyn", 	"Yerg", 	"Yk", 	"ZBa", 	"ZD", 	"ZG", 	"ZGal", 	"ZP", 	"ZSt", 	"Zdyn", 	"Zerg", 	"Zk", 	"aBa", 	"aD", 	"aG", 	"aGal", 	"aP", 	"aSt", 	"abA", 	"abC", 	"abampere", 	"abcoulomb", 	"adyn", 	"aerg", 	"ak", 	"attoBarye", 	"attoDebye", 	"attoGauss", 	"attoKayser", 	"attobarye", 	"attodebye", 	"attodyne", 	"attogal", 	"attogauss", 	"attokayser", 	"attopoise", 	"attostokes", 	"barye", 	"bases", 	"cBa", 	"cD", 	"cG", 	"cGal", 	"cP", 	"cSt", 	"cd", 	"cdyn", 	"centiBarye", 	"centiDebye", 	"centiGauss", 	"centiKayser", 	"centibarye", 	"centidebye", 	"centidyne", 	"centigal", 	"centigauss", 	"centikayser", 	"centimeter", 	"centipoise", 	"centistokes", 	"cerg", 	"ck", 	"cm", 	"dBa", 	"dD", 	"dG", 	"dGal", 	"dP", 	"dSt", 	"daBa", 	"daD", 	"daG", 	"daGal", 	"daP", 	"daSt", 	"dadyn", 	"daerg", 	"dak", 	"ddyn", 	"debye", 	"decaBarye", 	"decaDebye", 	"decaGauss", 	"decaKayser", 	"decabarye", 	"decadebye", 	"decadyne", 	"decagal", 	"decagauss", 	"decakayser", 	"decapoise", 	"decastokes", 	"deciBarye", 	"deciDebye", 	"deciGauss", 	"deciKayser", 	"decibarye", 	"decidebye", 	"decidyne", 	"decigal", 	"decigauss", 	"decikayser", 	"decipoise", 	"decistokes", 	"deg_C", 	"dekaBarye", 	"dekaDebye", 	"dekaGauss", 	"dekaKayser", 	"dekabarye", 	"dekadebye", 	"dekadyne", 	"dekagal", 	"dekagauss", 	"dekakayser", 	"dekapoise", 	"dekastokes", 	"derg", 	"division", 	"dk", 	"dyn", 	"dyne", 	"erg", 	"esu", 	"exaBarye", 	"exaDebye", 	"exaGauss", 	"exaKayser", 	"exabarye", 	"exadebye", 	"exadyne", 	"exagal", 	"exagauss", 	"exakayser", 	"exapoise", 	"exastokes", 	"fBa", 	"fD", 	"fG", 	"fGal", 	"fP", 	"fSt", 	"fdyn", 	"femtoBarye", 	"femtoDebye", 	"femtoGauss", 	"femtoKayser", 	"femtobarye", 	"femtodebye", 	"femtodyne", 	"femtogal", 	"femtogauss", 	"femtokayser", 	"femtopoise", 	"femtostokes", 	"ferg", 	"fk", 	"g", 	"gal", 	"gauss", 	"gigaBarye", 	"gigaDebye", 	"gigaGauss", 	"gigaKayser", 	"gigabarye", 	"gigadebye", 	"gigadyne", 	"gigagal", 	"gigagauss", 	"gigakayser", 	"gigapoise", 	"gigastokes", 	"hBa", 	"hD", 	"hG", 	"hGal", 	"hP", 	"hSt", 	"hdyn", 	"hectoBarye", 	"hectoDebye", 	"hectoGauss", 	"hectoKayser", 	"hectobarye", 	"hectodebye", 	"hectodyne", 	"hectogal", 	"hectogauss", 	"hectokayser", 	"hectopoise", 	"hectostokes", 	"herg", 	"hk", 	"k", 	"kBa", 	"kD", 	"kG", 	"kGal", 	"kP", 	"kSt", 	"kayser", 	"kdyn", 	"kerg", 	"kiloBarye", 	"kiloDebye", 	"kiloGauss", 	"kiloKayser", 	"kilobarye", 	"kilodebye", 	"kilodyne", 	"kilogal", 	"kilogauss", 	"kilokayser", 	"kilopoise", 	"kilostokes", 	"kk", 	"mBa", 	"mD", 	"mG", 	"mGal", 	"mP", 	"mSt", 	"mdyn", 	"megaBarye", 	"megaDebye", 	"megaGauss", 	"megaKayser", 	"megabarye", 	"megadebye", 	"megadyne", 	"megagal", 	"megagauss", 	"megakayser", 	"megapoise", 	"megastokes", 	"merg", 	"microBarye", 	"microDebye", 	"microGauss", 	"microKayser", 	"microbarye", 	"microdebye", 	"microdyne", 	"microgal", 	"microgauss", 	"microkayser", 	"micropoise", 	"microstokes", 	"milliBarye", 	"milliDebye", 	"milliGauss", 	"milliKayser", 	"millibarye", 	"millidebye", 	"millidyne", 	"milligal", 	"milligauss", 	"millikayser", 	"millipoise", 	"millistokes", 	"mk", 	"mol", 	"nBa", 	"nD", 	"nG", 	"nGal", 	"nP", 	"nSt", 	"nanoBarye", 	"nanoDebye", 	"nanoGauss", 	"nanoKayser", 	"nanobarye", 	"nanodebye", 	"nanodyne", 	"nanogal", 	"nanogauss", 	"nanokayser", 	"nanopoise", 	"nanostokes", 	"ndyn", 	"nerg", 	"nk", 	"pBa", 	"pD", 	"pG", 	"pGal", 	"pP", 	"pSt", 	"pdyn", 	"perg", 	"petaBarye", 	"petaDebye", 	"petaGauss", 	"petaKayser", 	"petabarye", 	"petadebye", 	"petadyne", 	"petagal", 	"petagauss", 	"petakayser", 	"petapoise", 	"petastokes", 	"picoBarye", 	"picoDebye", 	"picoGauss", 	"picoKayser", 	"picobarye", 	"picodebye", 	"picodyne", 	"picogal", 	"picogauss", 	"picokayser", 	"picopoise", 	"picostokes", 	"pk", 	"poise", 	"rad", 	"s", 	"sr", 	"statA", 	"statC", 	"statampere", 	"statcoulomb", 	"stokes", 	"teraBarye", 	"teraDebye", 	"teraGauss", 	"teraKayser", 	"terabarye", 	"teradebye", 	"teradyne", 	"teragal", 	"teragauss", 	"terakayser", 	"terapoise", 	"terastokes", 	"uBa", 	"uD", 	"uG", 	"uGal", 	"uP", 	"uSt", 	"udyn", 	"uerg", 	"uk", 	"yBa", 	"yD", 	"yG", 	"yGal", 	"yP", 	"ySt", 	"ydyn", 	"yerg", 	"yk", 	"yoctoBarye", 	"yoctoDebye", 	"yoctoGauss", 	"yoctoKayser", 	"yoctobarye", 	"yoctodebye", 	"yoctodyne", 	"yoctogal", 	"yoctogauss", 	"yoctokayser", 	"yoctopoise", 	"yoctostokes", 	"yottaBarye", 	"yottaDebye", 	"yottaGauss", 	"yottaKayser", 	"yottabarye", 	"yottadebye", 	"yottadyne", 	"yottagal", 	"yottagauss", 	"yottakayser", 	"yottapoise", 	"yottastokes", 	"zBa", 	"zD", 	"zG", 	"zGal", 	"zP", 	"zSt", 	"zdyn", 	"zeptoBarye", 	"zeptoDebye", 	"zeptoGauss", 	"zeptoKayser", 	"zeptobarye", 	"zeptodebye", 	"zeptodyne", 	"zeptogal", 	"zeptogauss", 	"zeptokayser", 	"zeptopoise", 	"zeptostokes", 	"zerg", 	"zettaBarye", 	"zettaDebye", 	"zettaGauss", 	"zettaKayser", 	"zettabarye", 	"zettadebye", 	"zettadyne", 	"zettagal", 	"zettagauss", 	"zettakayser", 	"zettapoise", 	"zettastokes", 	"zk", 	"AU", 	"B", 	"Da", 	"Dalton", 	"EAU", 	"EB", 	"EJy", 	"ER", 	"ERy", 	"Eadu", 	"Eau", 	"Eb", 	"Ebarn", 	"Ebeam", 	"Ebin", 	"Ebit", 	"Ebyte", 	"Echan", 	"Ecount", 	"Ect", 	"EiB", 	"Eib", 	"Eibit", 	"Eibyte", 	"Elyr", 	"Epc", 	"Eph", 	"Ephoton", 	"Epix", 	"Epixel", 	"Eu", 	"Evox", 	"Evoxel", 	"GAU", 	"GB", 	"GJy", 	"GR", 	"GRy", 	"Gadu", 	"Gau", 	"Gb", 	"Gbarn", 	"Gbeam", 	"Gbin", 	"Gbit", 	"Gbyte", 	"Gchan", 	"Gcount", 	"Gct", 	"GiB", 	"Gib", 	"Gibit", 	"Gibyte", 	"Glyr", 	"Gpc", 	"Gph", 	"Gphoton", 	"Gpix", 	"Gpixel", 	"Gu", 	"Gvox", 	"Gvoxel", 	"Jansky", 	"Jy", 	"KiB", 	"Kib", 	"Kibit", 	"Kibyte", 	"L_sun", 	"Lsun", 	"MAU", 	"MB", 	"MJy", 	"MR", 	"MRy", 	"M_e", 	"M_earth", 	"M_jup", 	"M_jupiter", 	"M_p", 	"M_sun", 	"Madu", 	"Mau", 	"Mb", 	"Mbarn", 	"Mbeam", 	"Mbin", 	"Mbit", 	"Mbyte", 	"Mchan", 	"Mcount", 	"Mct", 	"Mearth", 	"MiB", 	"Mib", 	"Mibit", 	"Mibyte", 	"Mjup", 	"Mjupiter", 	"Mlyr", 	"Mpc", 	"Mph", 	"Mphoton", 	"Mpix", 	"Mpixel", 	"Msun", 	"Mu", 	"Mvox", 	"Mvoxel", 	"PAU", 	"PB", 	"PJy", 	"PR", 	"PRy", 	"Padu", 	"Pau", 	"Pb", 	"Pbarn", 	"Pbeam", 	"Pbin", 	"Pbit", 	"Pbyte", 	"Pchan", 	"Pcount", 	"Pct", 	"PiB", 	"Pib", 	"Pibit", 	"Pibyte", 	"Plyr", 	"Ppc", 	"Pph", 	"Pphoton", 	"Ppix", 	"Ppixel", 	"Pu", 	"Pvox", 	"Pvoxel", 	"R", 	"R_earth", 	"R_jup", 	"R_jupiter", 	"R_sun", 	"Rayleigh", 	"Rearth", 	"Rjup", 	"Rjupiter", 	"Rsun", 	"Ry", 	"Sun", 	"TAU", 	"TB", 	"TJy", 	"TR", 	"TRy", 	"Tadu", 	"Tau", 	"Tb", 	"Tbarn", 	"Tbeam", 	"Tbin", 	"Tbit", 	"Tbyte", 	"Tchan", 	"Tcount", 	"Tct", 	"TiB", 	"Tib", 	"Tibit", 	"Tibyte", 	"Tlyr", 	"Tpc", 	"Tph", 	"Tphoton", 	"Tpix", 	"Tpixel", 	"Tu", 	"Tvox", 	"Tvoxel", 	"YAU", 	"YB", 	"YJy", 	"YR", 	"YRy", 	"Yadu", 	"Yau", 	"Yb", 	"Ybarn", 	"Ybeam", 	"Ybin", 	"Ybit", 	"Ybyte", 	"Ychan", 	"Ycount", 	"Yct", 	"Ylyr", 	"Ypc", 	"Yph", 	"Yphoton", 	"Ypix", 	"Ypixel", 	"Yu", 	"Yvox", 	"Yvoxel", 	"ZAU", 	"ZB", 	"ZJy", 	"ZR", 	"ZRy", 	"Zadu", 	"Zau", 	"Zb", 	"Zbarn", 	"Zbeam", 	"Zbin", 	"Zbit", 	"Zbyte", 	"Zchan", 	"Zcount", 	"Zct", 	"Zlyr", 	"Zpc", 	"Zph", 	"Zphoton", 	"Zpix", 	"Zpixel", 	"Zu", 	"Zvox", 	"Zvoxel", 	"aAU", 	"aB", 	"aJy", 	"aR", 	"aRy", 	"aadu", 	"aau", 	"ab", 	"abarn", 	"abeam", 	"abin", 	"abit", 	"abyte", 	"achan", 	"acount", 	"act", 	"adu", 	"alyr", 	"apc", 	"aph", 	"aphoton", 	"apix", 	"apixel", 	"astronomical_unit", 	"attoDa", 	"attoDalton", 	"attoJansky", 	"attoRayleigh", 	"attoastronomical_unit", 	"attobarn", 	"attobit", 	"attobyte", 	"attocount", 	"attojansky", 	"attolightyear", 	"attoparsec", 	"attophoton", 	"attopixel", 	"attorayleigh", 	"attorydberg", 	"attovoxel", 	"au", 	"avox", 	"avoxel", 	"b", 	"barn", 	"beam", 	"bin", 	"bit", 	"byte", 	"cAU", 	"cB", 	"cJy", 	"cR", 	"cRy", 	"cadu", 	"cau", 	"cb", 	"cbarn", 	"cbeam", 	"cbin", 	"cbit", 	"cbyte", 	"cchan", 	"ccount", 	"cct", 	"centiDa", 	"centiDalton", 	"centiJansky", 	"centiRayleigh", 	"centiastronomical_unit", 	"centibarn", 	"centibit", 	"centibyte", 	"centicount", 	"centijansky", 	"centilightyear", 	"centiparsec", 	"centiphoton", 	"centipixel", 	"centirayleigh", 	"centirydberg", 	"centivoxel", 	"chan", 	"clyr", 	"count", 	"cpc", 	"cph", 	"cphoton", 	"cpix", 	"cpixel", 	"ct", 	"cu", 	"cvox", 	"cvoxel", 	"cy", 	"cycle", 	"dAU", 	"dJy", 	"dR", 	"dRy", 	"daAU", 	"daB", 	"daJy", 	"daR", 	"daRy", 	"daadu", 	"daau", 	"dab", 	"dabarn", 	"dabeam", 	"dabin", 	"dabit", 	"dabyte", 	"dachan", 	"dacount", 	"dact", 	"dadu", 	"dalyr", 	"dapc", 	"daph", 	"daphoton", 	"dapix", 	"dapixel", 	"dau", 	"davox", 	"davoxel", 	"db", 	"dbarn", 	"dbeam", 	"dbin", 	"dbit", 	"dchan", 	"dcount", 	"dct", 	"decaDa", 	"decaDalton", 	"decaJansky", 	"decaRayleigh", 	"decaastronomical_unit", 	"decabarn", 	"decabit", 	"decabyte", 	"decacount", 	"decajansky", 	"decalightyear", 	"decaparsec", 	"decaphoton", 	"decapixel", 	"decarayleigh", 	"decarydberg", 	"decavoxel", 	"deciDa", 	"deciDalton", 	"deciJansky", 	"deciRayleigh", 	"deciastronomical_unit", 	"decibarn", 	"decibit", 	"decibyte", 	"decicount", 	"decijansky", 	"decilightyear", 	"deciparsec", 	"deciphoton", 	"decipixel", 	"decirayleigh", 	"decirydberg", 	"decivoxel", 	"dekaDa", 	"dekaDalton", 	"dekaJansky", 	"dekaRayleigh", 	"dekaastronomical_unit", 	"dekabarn", 	"dekabit", 	"dekabyte", 	"dekacount", 	"dekajansky", 	"dekalightyear", 	"dekaparsec", 	"dekaphoton", 	"dekapixel", 	"dekarayleigh", 	"dekarydberg", 	"dekavoxel", 	"division", 	"dlyr", 	"dpc", 	"dph", 	"dphoton", 	"dpix", 	"dpixel", 	"du", 	"dvox", 	"dvoxel", 	"earthMass", 	"earthRad", 	"electron", 	"exaDa", 	"exaDalton", 	"exaJansky", 	"exaRayleigh", 	"exaastronomical_unit", 	"exabarn", 	"exabit", 	"exabyte", 	"exacount", 	"exajansky", 	"exalightyear", 	"exaparsec", 	"exaphoton", 	"exapixel", 	"exarayleigh", 	"exarydberg", 	"exavoxel", 	"exbibit", 	"exbibyte", 	"fAU", 	"fB", 	"fJy", 	"fR", 	"fRy", 	"fadu", 	"fau", 	"fb", 	"fbarn", 	"fbeam", 	"fbin", 	"fbit", 	"fbyte", 	"fchan", 	"fcount", 	"fct", 	"femtoDa", 	"femtoDalton", 	"femtoJansky", 	"femtoRayleigh", 	"femtoastronomical_unit", 	"femtobarn", 	"femtobit", 	"femtobyte", 	"femtocount", 	"femtojansky", 	"femtolightyear", 	"femtoparsec", 	"femtophoton", 	"femtopixel", 	"femtorayleigh", 	"femtorydberg", 	"femtovoxel", 	"flyr", 	"fpc", 	"fph", 	"fphoton", 	"fpix", 	"fpixel", 	"fu", 	"fvox", 	"fvoxel", 	"gibibit", 	"gibibyte", 	"gigaDa", 	"gigaDalton", 	"gigaJansky", 	"gigaRayleigh", 	"gigaastronomical_unit", 	"gigabarn", 	"gigabit", 	"gigabyte", 	"gigacount", 	"gigajansky", 	"gigalightyear", 	"gigaparsec", 	"gigaphoton", 	"gigapixel", 	"gigarayleigh", 	"gigarydberg", 	"gigavoxel", 	"hAU", 	"hB", 	"hJy", 	"hR", 	"hRy", 	"hadu", 	"hau", 	"hb", 	"hbarn", 	"hbeam", 	"hbin", 	"hbit", 	"hbyte", 	"hchan", 	"hcount", 	"hct", 	"hectoDa", 	"hectoDalton", 	"hectoJansky", 	"hectoRayleigh", 	"hectoastronomical_unit", 	"hectobarn", 	"hectobit", 	"hectobyte", 	"hectocount", 	"hectojansky", 	"hectolightyear", 	"hectoparsec", 	"hectophoton", 	"hectopixel", 	"hectorayleigh", 	"hectorydberg", 	"hectovoxel", 	"hlyr", 	"hpc", 	"hph", 	"hphoton", 	"hpix", 	"hpixel", 	"hu", 	"hvox", 	"hvoxel", 	"jansky", 	"jupiterMass", 	"jupiterRad", 	"kAU", 	"kB", 	"kJy", 	"kR", 	"kRy", 	"kadu", 	"kau", 	"kb", 	"kbarn", 	"kbeam", 	"kbin", 	"kbit", 	"kbyte", 	"kchan", 	"kcount", 	"kct", 	"kibibit", 	"kibibyte", 	"kiloDa", 	"kiloDalton", 	"kiloJansky", 	"kiloRayleigh", 	"kiloastronomical_unit", 	"kilobarn", 	"kilobit", 	"kilobyte", 	"kilocount", 	"kilojansky", 	"kilolightyear", 	"kiloparsec", 	"kilophoton", 	"kilopixel", 	"kilorayleigh", 	"kilorydberg", 	"kilovoxel", 	"klyr", 	"kpc", 	"kph", 	"kphoton", 	"kpix", 	"kpixel", 	"ku", 	"kvox", 	"kvoxel", 	"lightyear", 	"lyr", 	"mAU", 	"mB", 	"mJy", 	"mR", 	"mRy", 	"madu", 	"mau", 	"mb", 	"mbarn", 	"mbeam", 	"mbin", 	"mbit", 	"mbyte", 	"mchan", 	"mcount", 	"mct", 	"mebibit", 	"mebibyte", 	"megaDa", 	"megaDalton", 	"megaJansky", 	"megaRayleigh", 	"megaastronomical_unit", 	"megabarn", 	"megabit", 	"megabyte", 	"megacount", 	"megajansky", 	"megalightyear", 	"megaparsec", 	"megaphoton", 	"megapixel", 	"megarayleigh", 	"megarydberg", 	"megavoxel", 	"microDa", 	"microDalton", 	"microJansky", 	"microRayleigh", 	"microastronomical_unit", 	"microbarn", 	"microbit", 	"microbyte", 	"microcount", 	"microjansky", 	"microlightyear", 	"microparsec", 	"microphoton", 	"micropixel", 	"microrayleigh", 	"microrydberg", 	"microvoxel", 	"milliDa", 	"milliDalton", 	"milliJansky", 	"milliRayleigh", 	"milliastronomical_unit", 	"millibarn", 	"millibit", 	"millibyte", 	"millicount", 	"millijansky", 	"millilightyear", 	"milliparsec", 	"milliphoton", 	"millipixel", 	"millirayleigh", 	"millirydberg", 	"millivoxel", 	"mlyr", 	"mpc", 	"mph", 	"mphoton", 	"mpix", 	"mpixel", 	"mu", 	"mvox", 	"mvoxel", 	"nAU", 	"nB", 	"nJy", 	"nR", 	"nRy", 	"nadu", 	"nanoDa", 	"nanoDalton", 	"nanoJansky", 	"nanoRayleigh", 	"nanoastronomical_unit", 	"nanobarn", 	"nanobit", 	"nanobyte", 	"nanocount", 	"nanojansky", 	"nanolightyear", 	"nanoparsec", 	"nanophoton", 	"nanopixel", 	"nanorayleigh", 	"nanorydberg", 	"nanovoxel", 	"nau", 	"nb", 	"nbarn", 	"nbeam", 	"nbin", 	"nbit", 	"nbyte", 	"nchan", 	"ncount", 	"nct", 	"nlyr", 	"npc", 	"nph", 	"nphoton", 	"npix", 	"npixel", 	"nu", 	"nvox", 	"nvoxel", 	"pAU", 	"pB", 	"pJy", 	"pR", 	"pRy", 	"padu", 	"parsec", 	"pau", 	"pb", 	"pbarn", 	"pbeam", 	"pbin", 	"pbit", 	"pbyte", 	"pc", 	"pchan", 	"pebibit", 	"pebibyte", 	"petaDa", 	"petaDalton", 	"petaJansky", 	"petaRayleigh", 	"petaastronomical_unit", 	"petabarn", 	"petabit", 	"petabyte", 	"petacount", 	"petajansky", 	"petalightyear", 	"petaparsec", 	"petaphoton", 	"petapixel", 	"petarayleigh", 	"petarydberg", 	"petavoxel", 	"ph", 	"photon", 	"picoDa", 	"picoDalton", 	"picoJansky", 	"picoRayleigh", 	"picoastronomical_unit", 	"picobarn", 	"picobit", 	"picobyte", 	"picocount", 	"picojansky", 	"picolightyear", 	"picoparsec", 	"picophoton", 	"picopixel", 	"picorayleigh", 	"picorydberg", 	"picovoxel", 	"pix", 	"pixel", 	"plyr", 	"ppc", 	"pph", 	"pphoton", 	"ppix", 	"ppixel", 	"pu", 	"pvox", 	"pvoxel", 	"rayleigh", 	"rydberg", 	"solLum", 	"solMass", 	"solRad", 	"tebibit", 	"tebibyte", 	"teraDa", 	"teraDalton", 	"teraJansky", 	"teraRayleigh", 	"teraastronomical_unit", 	"terabarn", 	"terabit", 	"terabyte", 	"teracount", 	"terajansky", 	"teralightyear", 	"teraparsec", 	"teraphoton", 	"terapixel", 	"terarayleigh", 	"terarydberg", 	"teravoxel", 	"u", 	"uAU", 	"uB", 	"uJy", 	"uR", 	"uRy", 	"uadu", 	"uau", 	"ub", 	"ubarn", 	"ubeam", 	"ubin", 	"ubit", 	"ubyte", 	"uchan", 	"ucount", 	"uct", 	"ulyr", 	"upc", 	"uph", 	"uphoton", 	"upix", 	"upixel", 	"uu", 	"uvox", 	"uvoxel", 	"vox", 	"voxel", 	"yAU", 	"yB", 	"yJy", 	"yR", 	"yRy", 	"yadu", 	"yau", 	"yb", 	"ybarn", 	"ybeam", 	"ybin", 	"ybit", 	"ybyte", 	"ychan", 	"ycount", 	"yct", 	"ylyr", 	"yoctoDa", 	"yoctoDalton", 	"yoctoJansky", 	"yoctoRayleigh", 	"yoctoastronomical_unit", 	"yoctobarn", 	"yoctobit", 	"yoctobyte", 	"yoctocount", 	"yoctojansky", 	"yoctolightyear", 	"yoctoparsec", 	"yoctophoton", 	"yoctopixel", 	"yoctorayleigh", 	"yoctorydberg", 	"yoctovoxel", 	"yottaDa", 	"yottaDalton", 	"yottaJansky", 	"yottaRayleigh", 	"yottaastronomical_unit", 	"yottabarn", 	"yottabit", 	"yottabyte", 	"yottacount", 	"yottajansky", 	"yottalightyear", 	"yottaparsec", 	"yottaphoton", 	"yottapixel", 	"yottarayleigh", 	"yottarydberg", 	"yottavoxel", 	"ypc", 	"yph", 	"yphoton", 	"ypix", 	"ypixel", 	"yu", 	"yvox", 	"yvoxel", 	"zAU", 	"zB", 	"zJy", 	"zR", 	"zRy", 	"zadu", 	"zau", 	"zb", 	"zbarn", 	"zbeam", 	"zbin", 	"zbit", 	"zbyte", 	"zchan", 	"zcount", 	"zct", 	"zeptoDa", 	"zeptoDalton", 	"zeptoJansky", 	"zeptoRayleigh", 	"zeptoastronomical_unit", 	"zeptobarn", 	"zeptobit", 	"zeptobyte", 	"zeptocount", 	"zeptojansky", 	"zeptolightyear", 	"zeptoparsec", 	"zeptophoton", 	"zeptopixel", 	"zeptorayleigh", 	"zeptorydberg", 	"zeptovoxel", 	"zettaDa", 	"zettaDalton", 	"zettaJansky", 	"zettaRayleigh", 	"zettaastronomical_unit", 	"zettabarn", 	"zettabit", 	"zettabyte", 	"zettacount", 	"zettajansky", 	"zettalightyear", 	"zettaparsec", 	"zettaphoton", 	"zettapixel", 	"zettarayleigh", 	"zettarydberg", 	"zettavoxel", 	"zlyr", 	"zpc", 	"zph", 	"zphoton", 	"zpix", 	"zpixel", 	"zu", 	"zvox", 	"zvoxel"), suffix=r'\b'),
             Keyword.Type),
        ],
        'builtins': [
            (words(("resolution", "steps", "emit_spike", "print", "println", "exp", "ln", "log10", "cosh", "sinh", "tanh", "info", "warning", "random", "randomInt", "expm1", "delta", "clip", "max", "min", "integrate_odes", "convolve", "true", "True", "false", "False"),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
        ],
        'numbers': [
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'\d+j?', Number.Integer)
        ],
        'name': [
            ('[a-zA-Z_]\w*', Name),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single')
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double)
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single)
        ],
    }


lexers["NESTML"] = NESTMLLexer(startinline=True)
lexers["nestml"] = NESTMLLexer(startinline=True)


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../doc/sphinx-apidoc'))
sys.path.insert(0, os.path.abspath('doc/sphinx-apidoc'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('pynestml'))
sys.path.insert(0, os.path.abspath('pynestml/codegeneration'))


os.system("sphinx-apidoc --module-first -o "
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pynestml')
 + " "
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pynestml'))	# in-source generation of necessary .rst files


import fnmatch
import os

static_docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Searching in: " + str(static_docs_dir))
sys.path.insert(0, os.path.join(static_docs_dir, "sphinx-apidoc"))
sys.path.insert(0, os.path.join(static_docs_dir, "sphinx-apidoc/pynestml_toolchain"))
sys.path.insert(0, os.path.join(static_docs_dir, "sphinx-apidoc/"))
matches = []
for root, dirnames, filenames in os.walk(static_docs_dir):
    for filename in fnmatch.filter(filenames, '*.rst'):
            matches.append(os.path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.pdf'):
            matches.append(os.path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.png'):
            matches.append(os.path.join(root, filename))
print("Matches:")
print(matches)

"""
import glob
/home/docs/checkouts/readthedocs.org/user_builds/nestml-api-documentation/checkouts/latest/doc/sphinx-apidoc
fns = glob.glob(os.path.join(os.path.basename(os.path.basename("/home/docs/checkouts/readthedocs.org/user_builds/nestml-api-documentation/checkouts/latest/doc/sphinx-apidoc")), "*.rst"), recursive=True)
print(os.path.join(os.path.basename(os.path.basename(os.path.abspath(__file__))), "*.rst"))
print(fns)
fns = [ fn for fn in fns if fn.endswith(".rst") and not "sphinx-apidoc" in fn ]
print(fns)
"""
for fn in matches:
	if "sphinx-apidoc" in fn:
		continue
	fn_from = fn
	fn_to = os.path.join(static_docs_dir, "sphinx-apidoc", fn[len(static_docs_dir)+1:])
	print("From " + fn_from + " to " + fn_to)
	os.system('install -v -D ' + fn_from + " " + fn_to)
#os.system('for i in `find .. -name "*.rst"` ; do if [[ ${i} != *"sphinx-apidoc"* ]] ; then install -v -D ${i} ${i/\.\.\//}; fi ; done')

"""os.system('cp -v '
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contents.rst')
 + ' '
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pynestml/contents.rst'))	# copy master file into source directory as sphinx needs it there"""

os.system('cp -v '
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pynestml/*.rst')
 + ' '
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '.'))	# copy master file into source directory as sphinx needs it there

os.system('cp -v '
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '../*.rst')
 + ' '
 + os.path.join(os.path.dirname(os.path.abspath(__file__)), '.'))	# copy master file into source directory as sphinx needs it there

# The master toctree document.
master_doc = "index"

source_suffix = ['.rst']


# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
]

mathjax_path = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS-MML_HTMLorMML"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
# source_suffix = '.rst'

# General information about the project.
project = u'NESTML documentation'
copyright = u'2004, nest-simulator'
author = u'nest-simulator'


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.0.0'
# The full version, including alpha/beta/rc tagss
release = '1.0.0'
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'manni'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# add numbered figure link
numfig = True

numfig_secnum_depth = (2)
numfig_format = {'figure': 'Figure %s', 'table': 'Table %s',
                 'code-block': 'Code Block %s'}
# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_theme_options = {'logo_only': True}
html_logo = "nestml-logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', 'nestml-logo']

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'NESTMLdoc'

html_show_sphinx = False
html_show_copyright = False

# This way works for ReadTheDocs
# With this local 'make html' is broken!
github_doc_root = ''

intersphinx_mapping = {'https://docs.python.org/': None}


def setup(app):
    app.add_stylesheet('css/custom.css')
    app.add_stylesheet('css/pygments.css')
    app.add_javascript("js/custom.js")


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'NESTML-doc.tex', u'NESTML documentation',
     u'NESTML documentation', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'nestml-doc', u'NESTML documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'NESTML-doc', u'NESTML documentation',
     author, 'NESTML-doc', 'NESTML documentation',
     'Miscellaneous'),
]

# -- Options for readthedocs ----------------------------------------------
# on_rtd = os.environ.get('READTHEDOCS') == 'True'
# if on_rtd:
#    html_theme = 'alabaster'
# else:
#    html_theme = 'nat'
