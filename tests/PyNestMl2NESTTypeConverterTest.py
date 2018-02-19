import unittest

from astropy import units

from pynestml.codegeneration.PyNestMl2NESTTypeConverter import NESTML2NESTTypeConverter
from pynestml.modelprocessor.BooleanTypeSymbol import BooleanTypeSymbol
from pynestml.modelprocessor.IntegerTypeSymbol import IntegerTypeSymbol
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol
from pynestml.modelprocessor.StringTypeSymbol import StringTypeSymbol
from pynestml.modelprocessor.UnitType import UnitType
from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
from pynestml.modelprocessor.VoidTypeSymbol import VoidTypeSymbol

PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()

convert = NESTML2NESTTypeConverter.convert


class PyNestMl2NESTTypeConverterTest(unittest.TestCase):

    def testBooleanType(self):
        bts = BooleanTypeSymbol()
        result = convert(bts)
        self.assertEqual(result, 'bool')
        return

    def testRealType(self):
        rts = RealTypeSymbol()
        result = convert(rts)
        self.assertEqual(result, 'double')

    def testVoidType(self):
        vts = VoidTypeSymbol()
        result = convert(vts)
        self.assertEqual(result, 'void')

    def testStringType(self):
        sts = StringTypeSymbol()
        result = convert(sts)
        self.assertEqual(result, 'std::string')

    def testIntegerType(self):
        its = IntegerTypeSymbol()
        result = convert(its)
        self.assertEqual(result, 'long')

    def testUnitType(self):
        ms_unit = UnitType(_name=str(units.ms), _unit=units.ms)
        uts = UnitTypeSymbol(_unit=ms_unit)
        result = convert(uts)
        self.assertEqual(result, 'double')
