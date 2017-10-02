# Generated from pynestml/src/main/grammars/org/PyNESTML.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"S\u027f\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4")
        buf.write(u"\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r")
        buf.write(u"\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22")
        buf.write(u"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4")
        buf.write(u"\30\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35")
        buf.write(u"\t\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4")
        buf.write(u"$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t")
        buf.write(u",\4-\t-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63")
        buf.write(u"\t\63\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\4")
        buf.write(u"9\t9\4:\t:\4;\t;\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@\4A\tA")
        buf.write(u"\4B\tB\4C\tC\4D\tD\4E\tE\4F\tF\4G\tG\4H\tH\4I\tI\4J\t")
        buf.write(u"J\4K\tK\4L\tL\4M\tM\4N\tN\4O\tO\4P\tP\4Q\tQ\4R\tR\4S")
        buf.write(u"\tS\4T\tT\4U\tU\4V\tV\4W\tW\3\2\3\2\3\2\3\2\3\2\3\2\3")
        buf.write(u"\2\3\2\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\4\3\4\3\4\3\4\3")
        buf.write(u"\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\6\3\6\3")
        buf.write(u"\6\3\7\3\7\3\b\3\b\3\t\3\t\3\t\3\n\3\n\3\13\3\13\3\f")
        buf.write(u"\3\f\3\r\3\r\3\16\3\16\3\17\3\17\3\17\3\17\3\20\3\20")
        buf.write(u"\3\21\3\21\3\21\3\21\3\22\3\22\3\23\3\23\3\24\3\24\3")
        buf.write(u"\25\3\25\3\26\3\26\3\26\3\27\3\27\3\27\3\30\3\30\3\31")
        buf.write(u"\3\31\3\31\3\32\3\32\3\32\3\33\3\33\3\33\3\34\3\34\3")
        buf.write(u"\34\3\35\3\35\3\35\3\36\3\36\3\37\3\37\3\37\3\37\3 \3")
        buf.write(u" \3 \3!\3!\3\"\3\"\3#\3#\3#\3#\3#\3#\3#\3#\3#\3#\3#\3")
        buf.write(u"$\3$\3$\3$\3$\3$\3$\3$\3$\3%\3%\3&\3&\3\'\3\'\3\'\3\'")
        buf.write(u"\3\'\3\'\3(\3(\3(\3)\3)\3)\3*\3*\3*\3+\3+\3+\3,\3,\3")
        buf.write(u"-\3-\3.\3.\3.\3/\3/\3/\3\60\3\60\3\60\3\60\3\60\3\60")
        buf.write(u"\3\60\3\61\3\61\3\61\3\62\3\62\3\62\3\62\3\62\3\63\3")
        buf.write(u"\63\3\63\3\63\3\63\3\64\3\64\3\64\3\64\3\65\3\65\3\65")
        buf.write(u"\3\66\3\66\3\66\3\66\3\67\3\67\3\67\3\67\3\67\38\38\3")
        buf.write(u"8\38\38\38\39\39\39\39\39\39\39\3:\3:\3:\3:\3:\3:\3;")
        buf.write(u"\3;\3;\3;\3;\3;\3;\3;\3;\3;\3;\3<\3<\3<\3<\3<\3<\3<\3")
        buf.write(u"<\3<\3<\3=\3=\3=\3=\3=\3=\3=\3=\3=\3=\3=\3=\3=\3=\3=")
        buf.write(u"\3>\3>\3>\3>\3>\3>\3>\3?\3?\3?\3?\3?\3?\3?\3?\3?\3?\3")
        buf.write(u"@\3@\3@\3@\3@\3@\3A\3A\3A\3B\3B\3B\3B\3B\3B\3B\3B\3C")
        buf.write(u"\3C\3C\3C\3C\3C\3D\3D\3D\3D\3D\3D\3D\3D\3D\3D\3D\3E\3")
        buf.write(u"E\3E\3E\3E\3E\3E\3E\3E\3E\3E\3F\3F\3F\3F\3F\3F\3F\3G")
        buf.write(u"\3G\7G\u01ee\nG\fG\16G\u01f1\13G\3G\3G\3H\3H\3H\3H\7")
        buf.write(u"H\u01f9\nH\fH\16H\u01fc\13H\3H\3H\3H\3H\3H\3H\3H\7H\u0205")
        buf.write(u"\nH\fH\16H\u0208\13H\3H\3H\3H\5H\u020d\nH\3H\3H\3I\3")
        buf.write(u"I\3I\5I\u0214\nI\3J\3J\3J\3J\3K\3K\5K\u021c\nK\3K\3K")
        buf.write(u"\3K\3K\3L\3L\3M\3M\3M\3M\3N\3N\3N\3N\3N\3N\3N\3N\3N\3")
        buf.write(u"N\3N\3N\3N\3N\3N\3N\3N\3N\5N\u023a\nN\3O\3O\5O\u023e")
        buf.write(u"\nO\3O\7O\u0241\nO\fO\16O\u0244\13O\3O\3O\3P\5P\u0249")
        buf.write(u"\nP\3P\7P\u024c\nP\fP\16P\u024f\13P\3Q\3Q\5Q\u0253\n")
        buf.write(u"Q\3R\3R\7R\u0257\nR\fR\16R\u025a\13R\3S\3S\5S\u025e\n")
        buf.write(u"S\3T\3T\5T\u0262\nT\3T\3T\3T\5T\u0267\nT\3T\5T\u026a")
        buf.write(u"\nT\3U\3U\5U\u026e\nU\3U\3U\3V\3V\5V\u0274\nV\3V\3V\5")
        buf.write(u"V\u0278\nV\3W\3W\6W\u027c\nW\rW\16W\u027d\4\u01fa\u0206")
        buf.write(u"\2X\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27")
        buf.write(u"\r\31\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-")
        buf.write(u"\30/\31\61\32\63\33\65\34\67\359\36;\37= ?!A\"C#E$G%")
        buf.write(u"I&K\'M(O)Q*S+U,W-Y.[/]\60_\61a\62c\63e\64g\65i\66k\67")
        buf.write(u"m8o9q:s;u<w=y>{?}@\177A\u0081B\u0083C\u0085D\u0087E\u0089")
        buf.write(u"F\u008bG\u008dH\u008fI\u0091J\u0093K\u0095L\u0097M\u0099")
        buf.write(u"N\u009bO\u009dP\u009fQ\u00a1R\u00a3\2\u00a5S\u00a7\2")
        buf.write(u"\u00a9\2\u00ab\2\u00ad\2\3\2\n\4\2\f\f\17\17\4\2\13\13")
        buf.write(u"\"\"\6\2&&C\\aac|\7\2&&\62;C\\aac|\3\2\63;\3\2\62;\4")
        buf.write(u"\2GGgg\4\2--//\2\u028f\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3")
        buf.write(u"\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2")
        buf.write(u"\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2")
        buf.write(u"\2\2\2\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2")
        buf.write(u"\2\2\2!\3\2\2\2\2#\3\2\2\2\2%\3\2\2\2\2\'\3\2\2\2\2)")
        buf.write(u"\3\2\2\2\2+\3\2\2\2\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2\2")
        buf.write(u"\2\2\63\3\2\2\2\2\65\3\2\2\2\2\67\3\2\2\2\29\3\2\2\2")
        buf.write(u"\2;\3\2\2\2\2=\3\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2")
        buf.write(u"\2\2E\3\2\2\2\2G\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2")
        buf.write(u"\2\2\2O\3\2\2\2\2Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3")
        buf.write(u"\2\2\2\2Y\3\2\2\2\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2")
        buf.write(u"a\3\2\2\2\2c\3\2\2\2\2e\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2")
        buf.write(u"\2k\3\2\2\2\2m\3\2\2\2\2o\3\2\2\2\2q\3\2\2\2\2s\3\2\2")
        buf.write(u"\2\2u\3\2\2\2\2w\3\2\2\2\2y\3\2\2\2\2{\3\2\2\2\2}\3\2")
        buf.write(u"\2\2\2\177\3\2\2\2\2\u0081\3\2\2\2\2\u0083\3\2\2\2\2")
        buf.write(u"\u0085\3\2\2\2\2\u0087\3\2\2\2\2\u0089\3\2\2\2\2\u008b")
        buf.write(u"\3\2\2\2\2\u008d\3\2\2\2\2\u008f\3\2\2\2\2\u0091\3\2")
        buf.write(u"\2\2\2\u0093\3\2\2\2\2\u0095\3\2\2\2\2\u0097\3\2\2\2")
        buf.write(u"\2\u0099\3\2\2\2\2\u009b\3\2\2\2\2\u009d\3\2\2\2\2\u009f")
        buf.write(u"\3\2\2\2\2\u00a1\3\2\2\2\2\u00a5\3\2\2\2\3\u00af\3\2")
        buf.write(u"\2\2\5\u00b7\3\2\2\2\7\u00bc\3\2\2\2\t\u00c3\3\2\2\2")
        buf.write(u"\13\u00cb\3\2\2\2\r\u00d0\3\2\2\2\17\u00d2\3\2\2\2\21")
        buf.write(u"\u00d4\3\2\2\2\23\u00d7\3\2\2\2\25\u00d9\3\2\2\2\27\u00db")
        buf.write(u"\3\2\2\2\31\u00dd\3\2\2\2\33\u00df\3\2\2\2\35\u00e1\3")
        buf.write(u"\2\2\2\37\u00e5\3\2\2\2!\u00e7\3\2\2\2#\u00eb\3\2\2\2")
        buf.write(u"%\u00ed\3\2\2\2\'\u00ef\3\2\2\2)\u00f1\3\2\2\2+\u00f3")
        buf.write(u"\3\2\2\2-\u00f6\3\2\2\2/\u00f9\3\2\2\2\61\u00fb\3\2\2")
        buf.write(u"\2\63\u00fe\3\2\2\2\65\u0101\3\2\2\2\67\u0104\3\2\2\2")
        buf.write(u"9\u0107\3\2\2\2;\u010a\3\2\2\2=\u010c\3\2\2\2?\u0110")
        buf.write(u"\3\2\2\2A\u0113\3\2\2\2C\u0115\3\2\2\2E\u0117\3\2\2\2")
        buf.write(u"G\u0122\3\2\2\2I\u012b\3\2\2\2K\u012d\3\2\2\2M\u012f")
        buf.write(u"\3\2\2\2O\u0135\3\2\2\2Q\u0138\3\2\2\2S\u013b\3\2\2\2")
        buf.write(u"U\u013e\3\2\2\2W\u0141\3\2\2\2Y\u0143\3\2\2\2[\u0145")
        buf.write(u"\3\2\2\2]\u0148\3\2\2\2_\u014b\3\2\2\2a\u0152\3\2\2\2")
        buf.write(u"c\u0155\3\2\2\2e\u015a\3\2\2\2g\u015f\3\2\2\2i\u0163")
        buf.write(u"\3\2\2\2k\u0166\3\2\2\2m\u016a\3\2\2\2o\u016f\3\2\2\2")
        buf.write(u"q\u0175\3\2\2\2s\u017c\3\2\2\2u\u0182\3\2\2\2w\u018d")
        buf.write(u"\3\2\2\2y\u0197\3\2\2\2{\u01a6\3\2\2\2}\u01ad\3\2\2\2")
        buf.write(u"\177\u01b7\3\2\2\2\u0081\u01bd\3\2\2\2\u0083\u01c0\3")
        buf.write(u"\2\2\2\u0085\u01c8\3\2\2\2\u0087\u01ce\3\2\2\2\u0089")
        buf.write(u"\u01d9\3\2\2\2\u008b\u01e4\3\2\2\2\u008d\u01eb\3\2\2")
        buf.write(u"\2\u008f\u020c\3\2\2\2\u0091\u0213\3\2\2\2\u0093\u0215")
        buf.write(u"\3\2\2\2\u0095\u0219\3\2\2\2\u0097\u0221\3\2\2\2\u0099")
        buf.write(u"\u0223\3\2\2\2\u009b\u0239\3\2\2\2\u009d\u023b\3\2\2")
        buf.write(u"\2\u009f\u0248\3\2\2\2\u00a1\u0252\3\2\2\2\u00a3\u0254")
        buf.write(u"\3\2\2\2\u00a5\u025d\3\2\2\2\u00a7\u0269\3\2\2\2\u00a9")
        buf.write(u"\u026d\3\2\2\2\u00ab\u0271\3\2\2\2\u00ad\u0279\3\2\2")
        buf.write(u"\2\u00af\u00b0\7k\2\2\u00b0\u00b1\7p\2\2\u00b1\u00b2")
        buf.write(u"\7v\2\2\u00b2\u00b3\7g\2\2\u00b3\u00b4\7i\2\2\u00b4\u00b5")
        buf.write(u"\7g\2\2\u00b5\u00b6\7t\2\2\u00b6\4\3\2\2\2\u00b7\u00b8")
        buf.write(u"\7t\2\2\u00b8\u00b9\7g\2\2\u00b9\u00ba\7c\2\2\u00ba\u00bb")
        buf.write(u"\7n\2\2\u00bb\6\3\2\2\2\u00bc\u00bd\7u\2\2\u00bd\u00be")
        buf.write(u"\7v\2\2\u00be\u00bf\7t\2\2\u00bf\u00c0\7k\2\2\u00c0\u00c1")
        buf.write(u"\7p\2\2\u00c1\u00c2\7i\2\2\u00c2\b\3\2\2\2\u00c3\u00c4")
        buf.write(u"\7d\2\2\u00c4\u00c5\7q\2\2\u00c5\u00c6\7q\2\2\u00c6\u00c7")
        buf.write(u"\7n\2\2\u00c7\u00c8\7g\2\2\u00c8\u00c9\7c\2\2\u00c9\u00ca")
        buf.write(u"\7p\2\2\u00ca\n\3\2\2\2\u00cb\u00cc\7x\2\2\u00cc\u00cd")
        buf.write(u"\7q\2\2\u00cd\u00ce\7k\2\2\u00ce\u00cf\7f\2\2\u00cf\f")
        buf.write(u"\3\2\2\2\u00d0\u00d1\7*\2\2\u00d1\16\3\2\2\2\u00d2\u00d3")
        buf.write(u"\7+\2\2\u00d3\20\3\2\2\2\u00d4\u00d5\7,\2\2\u00d5\u00d6")
        buf.write(u"\7,\2\2\u00d6\22\3\2\2\2\u00d7\u00d8\7,\2\2\u00d8\24")
        buf.write(u"\3\2\2\2\u00d9\u00da\7\61\2\2\u00da\26\3\2\2\2\u00db")
        buf.write(u"\u00dc\7\'\2\2\u00dc\30\3\2\2\2\u00dd\u00de\7-\2\2\u00de")
        buf.write(u"\32\3\2\2\2\u00df\u00e0\7/\2\2\u00e0\34\3\2\2\2\u00e1")
        buf.write(u"\u00e2\7p\2\2\u00e2\u00e3\7q\2\2\u00e3\u00e4\7v\2\2\u00e4")
        buf.write(u"\36\3\2\2\2\u00e5\u00e6\7A\2\2\u00e6 \3\2\2\2\u00e7\u00e8")
        buf.write(u"\7k\2\2\u00e8\u00e9\7p\2\2\u00e9\u00ea\7h\2\2\u00ea\"")
        buf.write(u"\3\2\2\2\u00eb\u00ec\7\u0080\2\2\u00ec$\3\2\2\2\u00ed")
        buf.write(u"\u00ee\7(\2\2\u00ee&\3\2\2\2\u00ef\u00f0\7`\2\2\u00f0")
        buf.write(u"(\3\2\2\2\u00f1\u00f2\7~\2\2\u00f2*\3\2\2\2\u00f3\u00f4")
        buf.write(u"\7>\2\2\u00f4\u00f5\7>\2\2\u00f5,\3\2\2\2\u00f6\u00f7")
        buf.write(u"\7@\2\2\u00f7\u00f8\7@\2\2\u00f8.\3\2\2\2\u00f9\u00fa")
        buf.write(u"\7>\2\2\u00fa\60\3\2\2\2\u00fb\u00fc\7>\2\2\u00fc\u00fd")
        buf.write(u"\7?\2\2\u00fd\62\3\2\2\2\u00fe\u00ff\7?\2\2\u00ff\u0100")
        buf.write(u"\7?\2\2\u0100\64\3\2\2\2\u0101\u0102\7#\2\2\u0102\u0103")
        buf.write(u"\7?\2\2\u0103\66\3\2\2\2\u0104\u0105\7>\2\2\u0105\u0106")
        buf.write(u"\7@\2\2\u01068\3\2\2\2\u0107\u0108\7@\2\2\u0108\u0109")
        buf.write(u"\7?\2\2\u0109:\3\2\2\2\u010a\u010b\7@\2\2\u010b<\3\2")
        buf.write(u"\2\2\u010c\u010d\7c\2\2\u010d\u010e\7p\2\2\u010e\u010f")
        buf.write(u"\7f\2\2\u010f>\3\2\2\2\u0110\u0111\7q\2\2\u0111\u0112")
        buf.write(u"\7t\2\2\u0112@\3\2\2\2\u0113\u0114\7)\2\2\u0114B\3\2")
        buf.write(u"\2\2\u0115\u0116\7.\2\2\u0116D\3\2\2\2\u0117\u0118\7")
        buf.write(u"t\2\2\u0118\u0119\7g\2\2\u0119\u011a\7e\2\2\u011a\u011b")
        buf.write(u"\7q\2\2\u011b\u011c\7t\2\2\u011c\u011d\7f\2\2\u011d\u011e")
        buf.write(u"\7c\2\2\u011e\u011f\7d\2\2\u011f\u0120\7n\2\2\u0120\u0121")
        buf.write(u"\7g\2\2\u0121F\3\2\2\2\u0122\u0123\7h\2\2\u0123\u0124")
        buf.write(u"\7w\2\2\u0124\u0125\7p\2\2\u0125\u0126\7e\2\2\u0126\u0127")
        buf.write(u"\7v\2\2\u0127\u0128\7k\2\2\u0128\u0129\7q\2\2\u0129\u012a")
        buf.write(u"\7p\2\2\u012aH\3\2\2\2\u012b\u012c\7?\2\2\u012cJ\3\2")
        buf.write(u"\2\2\u012d\u012e\7=\2\2\u012eL\3\2\2\2\u012f\u0130\7")
        buf.write(u"u\2\2\u0130\u0131\7j\2\2\u0131\u0132\7c\2\2\u0132\u0133")
        buf.write(u"\7r\2\2\u0133\u0134\7g\2\2\u0134N\3\2\2\2\u0135\u0136")
        buf.write(u"\7-\2\2\u0136\u0137\7?\2\2\u0137P\3\2\2\2\u0138\u0139")
        buf.write(u"\7/\2\2\u0139\u013a\7?\2\2\u013aR\3\2\2\2\u013b\u013c")
        buf.write(u"\7,\2\2\u013c\u013d\7?\2\2\u013dT\3\2\2\2\u013e\u013f")
        buf.write(u"\7\61\2\2\u013f\u0140\7?\2\2\u0140V\3\2\2\2\u0141\u0142")
        buf.write(u"\7]\2\2\u0142X\3\2\2\2\u0143\u0144\7_\2\2\u0144Z\3\2")
        buf.write(u"\2\2\u0145\u0146\7]\2\2\u0146\u0147\7]\2\2\u0147\\\3")
        buf.write(u"\2\2\2\u0148\u0149\7_\2\2\u0149\u014a\7_\2\2\u014a^\3")
        buf.write(u"\2\2\2\u014b\u014c\7t\2\2\u014c\u014d\7g\2\2\u014d\u014e")
        buf.write(u"\7v\2\2\u014e\u014f\7w\2\2\u014f\u0150\7t\2\2\u0150\u0151")
        buf.write(u"\7p\2\2\u0151`\3\2\2\2\u0152\u0153\7k\2\2\u0153\u0154")
        buf.write(u"\7h\2\2\u0154b\3\2\2\2\u0155\u0156\7g\2\2\u0156\u0157")
        buf.write(u"\7n\2\2\u0157\u0158\7k\2\2\u0158\u0159\7h\2\2\u0159d")
        buf.write(u"\3\2\2\2\u015a\u015b\7g\2\2\u015b\u015c\7n\2\2\u015c")
        buf.write(u"\u015d\7u\2\2\u015d\u015e\7g\2\2\u015ef\3\2\2\2\u015f")
        buf.write(u"\u0160\7h\2\2\u0160\u0161\7q\2\2\u0161\u0162\7t\2\2\u0162")
        buf.write(u"h\3\2\2\2\u0163\u0164\7k\2\2\u0164\u0165\7p\2\2\u0165")
        buf.write(u"j\3\2\2\2\u0166\u0167\7\60\2\2\u0167\u0168\7\60\2\2\u0168")
        buf.write(u"\u0169\7\60\2\2\u0169l\3\2\2\2\u016a\u016b\7u\2\2\u016b")
        buf.write(u"\u016c\7v\2\2\u016c\u016d\7g\2\2\u016d\u016e\7r\2\2\u016e")
        buf.write(u"n\3\2\2\2\u016f\u0170\7y\2\2\u0170\u0171\7j\2\2\u0171")
        buf.write(u"\u0172\7k\2\2\u0172\u0173\7n\2\2\u0173\u0174\7g\2\2\u0174")
        buf.write(u"p\3\2\2\2\u0175\u0176\7p\2\2\u0176\u0177\7g\2\2\u0177")
        buf.write(u"\u0178\7w\2\2\u0178\u0179\7t\2\2\u0179\u017a\7q\2\2\u017a")
        buf.write(u"\u017b\7p\2\2\u017br\3\2\2\2\u017c\u017d\7u\2\2\u017d")
        buf.write(u"\u017e\7v\2\2\u017e\u017f\7c\2\2\u017f\u0180\7v\2\2\u0180")
        buf.write(u"\u0181\7g\2\2\u0181t\3\2\2\2\u0182\u0183\7r\2\2\u0183")
        buf.write(u"\u0184\7c\2\2\u0184\u0185\7t\2\2\u0185\u0186\7c\2\2\u0186")
        buf.write(u"\u0187\7o\2\2\u0187\u0188\7g\2\2\u0188\u0189\7v\2\2\u0189")
        buf.write(u"\u018a\7g\2\2\u018a\u018b\7t\2\2\u018b\u018c\7u\2\2\u018c")
        buf.write(u"v\3\2\2\2\u018d\u018e\7k\2\2\u018e\u018f\7p\2\2\u018f")
        buf.write(u"\u0190\7v\2\2\u0190\u0191\7g\2\2\u0191\u0192\7t\2\2\u0192")
        buf.write(u"\u0193\7p\2\2\u0193\u0194\7c\2\2\u0194\u0195\7n\2\2\u0195")
        buf.write(u"\u0196\7u\2\2\u0196x\3\2\2\2\u0197\u0198\7k\2\2\u0198")
        buf.write(u"\u0199\7p\2\2\u0199\u019a\7k\2\2\u019a\u019b\7v\2\2\u019b")
        buf.write(u"\u019c\7k\2\2\u019c\u019d\7c\2\2\u019d\u019e\7n\2\2\u019e")
        buf.write(u"\u019f\7a\2\2\u019f\u01a0\7x\2\2\u01a0\u01a1\7c\2\2\u01a1")
        buf.write(u"\u01a2\7n\2\2\u01a2\u01a3\7w\2\2\u01a3\u01a4\7g\2\2\u01a4")
        buf.write(u"\u01a5\7u\2\2\u01a5z\3\2\2\2\u01a6\u01a7\7w\2\2\u01a7")
        buf.write(u"\u01a8\7r\2\2\u01a8\u01a9\7f\2\2\u01a9\u01aa\7c\2\2\u01aa")
        buf.write(u"\u01ab\7v\2\2\u01ab\u01ac\7g\2\2\u01ac|\3\2\2\2\u01ad")
        buf.write(u"\u01ae\7g\2\2\u01ae\u01af\7s\2\2\u01af\u01b0\7w\2\2\u01b0")
        buf.write(u"\u01b1\7c\2\2\u01b1\u01b2\7v\2\2\u01b2\u01b3\7k\2\2\u01b3")
        buf.write(u"\u01b4\7q\2\2\u01b4\u01b5\7p\2\2\u01b5\u01b6\7u\2\2\u01b6")
        buf.write(u"~\3\2\2\2\u01b7\u01b8\7k\2\2\u01b8\u01b9\7p\2\2\u01b9")
        buf.write(u"\u01ba\7r\2\2\u01ba\u01bb\7w\2\2\u01bb\u01bc\7v\2\2\u01bc")
        buf.write(u"\u0080\3\2\2\2\u01bd\u01be\7>\2\2\u01be\u01bf\7/\2\2")
        buf.write(u"\u01bf\u0082\3\2\2\2\u01c0\u01c1\7e\2\2\u01c1\u01c2\7")
        buf.write(u"w\2\2\u01c2\u01c3\7t\2\2\u01c3\u01c4\7t\2\2\u01c4\u01c5")
        buf.write(u"\7g\2\2\u01c5\u01c6\7p\2\2\u01c6\u01c7\7v\2\2\u01c7\u0084")
        buf.write(u"\3\2\2\2\u01c8\u01c9\7u\2\2\u01c9\u01ca\7r\2\2\u01ca")
        buf.write(u"\u01cb\7k\2\2\u01cb\u01cc\7m\2\2\u01cc\u01cd\7g\2\2\u01cd")
        buf.write(u"\u0086\3\2\2\2\u01ce\u01cf\7k\2\2\u01cf\u01d0\7p\2\2")
        buf.write(u"\u01d0\u01d1\7j\2\2\u01d1\u01d2\7k\2\2\u01d2\u01d3\7")
        buf.write(u"d\2\2\u01d3\u01d4\7k\2\2\u01d4\u01d5\7v\2\2\u01d5\u01d6")
        buf.write(u"\7q\2\2\u01d6\u01d7\7t\2\2\u01d7\u01d8\7{\2\2\u01d8\u0088")
        buf.write(u"\3\2\2\2\u01d9\u01da\7g\2\2\u01da\u01db\7z\2\2\u01db")
        buf.write(u"\u01dc\7e\2\2\u01dc\u01dd\7k\2\2\u01dd\u01de\7v\2\2\u01de")
        buf.write(u"\u01df\7c\2\2\u01df\u01e0\7v\2\2\u01e0\u01e1\7q\2\2\u01e1")
        buf.write(u"\u01e2\7t\2\2\u01e2\u01e3\7{\2\2\u01e3\u008a\3\2\2\2")
        buf.write(u"\u01e4\u01e5\7q\2\2\u01e5\u01e6\7w\2\2\u01e6\u01e7\7")
        buf.write(u"v\2\2\u01e7\u01e8\7r\2\2\u01e8\u01e9\7w\2\2\u01e9\u01ea")
        buf.write(u"\7v\2\2\u01ea\u008c\3\2\2\2\u01eb\u01ef\7%\2\2\u01ec")
        buf.write(u"\u01ee\n\2\2\2\u01ed\u01ec\3\2\2\2\u01ee\u01f1\3\2\2")
        buf.write(u"\2\u01ef\u01ed\3\2\2\2\u01ef\u01f0\3\2\2\2\u01f0\u01f2")
        buf.write(u"\3\2\2\2\u01f1\u01ef\3\2\2\2\u01f2\u01f3\bG\2\2\u01f3")
        buf.write(u"\u008e\3\2\2\2\u01f4\u01f5\7\61\2\2\u01f5\u01f6\7,\2")
        buf.write(u"\2\u01f6\u01fa\3\2\2\2\u01f7\u01f9\13\2\2\2\u01f8\u01f7")
        buf.write(u"\3\2\2\2\u01f9\u01fc\3\2\2\2\u01fa\u01fb\3\2\2\2\u01fa")
        buf.write(u"\u01f8\3\2\2\2\u01fb\u01fd\3\2\2\2\u01fc\u01fa\3\2\2")
        buf.write(u"\2\u01fd\u01fe\7,\2\2\u01fe\u020d\7\61\2\2\u01ff\u0200")
        buf.write(u"\7$\2\2\u0200\u0201\7$\2\2\u0201\u0202\7$\2\2\u0202\u0206")
        buf.write(u"\3\2\2\2\u0203\u0205\13\2\2\2\u0204\u0203\3\2\2\2\u0205")
        buf.write(u"\u0208\3\2\2\2\u0206\u0207\3\2\2\2\u0206\u0204\3\2\2")
        buf.write(u"\2\u0207\u0209\3\2\2\2\u0208\u0206\3\2\2\2\u0209\u020a")
        buf.write(u"\7$\2\2\u020a\u020b\7$\2\2\u020b\u020d\7$\2\2\u020c\u01f4")
        buf.write(u"\3\2\2\2\u020c\u01ff\3\2\2\2\u020d\u020e\3\2\2\2\u020e")
        buf.write(u"\u020f\bH\2\2\u020f\u0090\3\2\2\2\u0210\u0211\7\17\2")
        buf.write(u"\2\u0211\u0214\7\f\2\2\u0212\u0214\t\2\2\2\u0213\u0210")
        buf.write(u"\3\2\2\2\u0213\u0212\3\2\2\2\u0214\u0092\3\2\2\2\u0215")
        buf.write(u"\u0216\t\3\2\2\u0216\u0217\3\2\2\2\u0217\u0218\bJ\2\2")
        buf.write(u"\u0218\u0094\3\2\2\2\u0219\u021b\7^\2\2\u021a\u021c\7")
        buf.write(u"\17\2\2\u021b\u021a\3\2\2\2\u021b\u021c\3\2\2\2\u021c")
        buf.write(u"\u021d\3\2\2\2\u021d\u021e\7\f\2\2\u021e\u021f\3\2\2")
        buf.write(u"\2\u021f\u0220\bK\2\2\u0220\u0096\3\2\2\2\u0221\u0222")
        buf.write(u"\7<\2\2\u0222\u0098\3\2\2\2\u0223\u0224\7g\2\2\u0224")
        buf.write(u"\u0225\7p\2\2\u0225\u0226\7f\2\2\u0226\u009a\3\2\2\2")
        buf.write(u"\u0227\u0228\7v\2\2\u0228\u0229\7t\2\2\u0229\u022a\7")
        buf.write(u"w\2\2\u022a\u023a\7g\2\2\u022b\u022c\7V\2\2\u022c\u022d")
        buf.write(u"\7t\2\2\u022d\u022e\7w\2\2\u022e\u023a\7g\2\2\u022f\u0230")
        buf.write(u"\7h\2\2\u0230\u0231\7c\2\2\u0231\u0232\7n\2\2\u0232\u0233")
        buf.write(u"\7u\2\2\u0233\u023a\7g\2\2\u0234\u0235\7H\2\2\u0235\u0236")
        buf.write(u"\7c\2\2\u0236\u0237\7n\2\2\u0237\u0238\7u\2\2\u0238\u023a")
        buf.write(u"\7g\2\2\u0239\u0227\3\2\2\2\u0239\u022b\3\2\2\2\u0239")
        buf.write(u"\u022f\3\2\2\2\u0239\u0234\3\2\2\2\u023a\u009c\3\2\2")
        buf.write(u"\2\u023b\u023d\7$\2\2\u023c\u023e\t\4\2\2\u023d\u023c")
        buf.write(u"\3\2\2\2\u023e\u0242\3\2\2\2\u023f\u0241\t\5\2\2\u0240")
        buf.write(u"\u023f\3\2\2\2\u0241\u0244\3\2\2\2\u0242\u0240\3\2\2")
        buf.write(u"\2\u0242\u0243\3\2\2\2\u0243\u0245\3\2\2\2\u0244\u0242")
        buf.write(u"\3\2\2\2\u0245\u0246\7$\2\2\u0246\u009e\3\2\2\2\u0247")
        buf.write(u"\u0249\t\4\2\2\u0248\u0247\3\2\2\2\u0249\u024d\3\2\2")
        buf.write(u"\2\u024a\u024c\t\5\2\2\u024b\u024a\3\2\2\2\u024c\u024f")
        buf.write(u"\3\2\2\2\u024d\u024b\3\2\2\2\u024d\u024e\3\2\2\2\u024e")
        buf.write(u"\u00a0\3\2\2\2\u024f\u024d\3\2\2\2\u0250\u0253\5\u00a3")
        buf.write(u"R\2\u0251\u0253\7\62\2\2\u0252\u0250\3\2\2\2\u0252\u0251")
        buf.write(u"\3\2\2\2\u0253\u00a2\3\2\2\2\u0254\u0258\t\6\2\2\u0255")
        buf.write(u"\u0257\t\7\2\2\u0256\u0255\3\2\2\2\u0257\u025a\3\2\2")
        buf.write(u"\2\u0258\u0256\3\2\2\2\u0258\u0259\3\2\2\2\u0259\u00a4")
        buf.write(u"\3\2\2\2\u025a\u0258\3\2\2\2\u025b\u025e\5\u00a7T\2\u025c")
        buf.write(u"\u025e\5\u00a9U\2\u025d\u025b\3\2\2\2\u025d\u025c\3\2")
        buf.write(u"\2\2\u025e\u00a6\3\2\2\2\u025f\u0262\5\u00a3R\2\u0260")
        buf.write(u"\u0262\7\62\2\2\u0261\u025f\3\2\2\2\u0261\u0260\3\2\2")
        buf.write(u"\2\u0261\u0262\3\2\2\2\u0262\u0263\3\2\2\2\u0263\u026a")
        buf.write(u"\5\u00adW\2\u0264\u0267\5\u00a3R\2\u0265\u0267\7\62\2")
        buf.write(u"\2\u0266\u0264\3\2\2\2\u0266\u0265\3\2\2\2\u0267\u0268")
        buf.write(u"\3\2\2\2\u0268\u026a\7\60\2\2\u0269\u0261\3\2\2\2\u0269")
        buf.write(u"\u0266\3\2\2\2\u026a\u00a8\3\2\2\2\u026b\u026e\5\u00a3")
        buf.write(u"R\2\u026c\u026e\5\u00a7T\2\u026d\u026b\3\2\2\2\u026d")
        buf.write(u"\u026c\3\2\2\2\u026e\u026f\3\2\2\2\u026f\u0270\5\u00ab")
        buf.write(u"V\2\u0270\u00aa\3\2\2\2\u0271\u0273\t\b\2\2\u0272\u0274")
        buf.write(u"\t\t\2\2\u0273\u0272\3\2\2\2\u0273\u0274\3\2\2\2\u0274")
        buf.write(u"\u0277\3\2\2\2\u0275\u0278\5\u00a3R\2\u0276\u0278\7\62")
        buf.write(u"\2\2\u0277\u0275\3\2\2\2\u0277\u0276\3\2\2\2\u0278\u00ac")
        buf.write(u"\3\2\2\2\u0279\u027b\7\60\2\2\u027a\u027c\t\7\2\2\u027b")
        buf.write(u"\u027a\3\2\2\2\u027c\u027d\3\2\2\2\u027d\u027b\3\2\2")
        buf.write(u"\2\u027d\u027e\3\2\2\2\u027e\u00ae\3\2\2\2\32\2\u01ef")
        buf.write(u"\u01fa\u0206\u020c\u0213\u021b\u0239\u023d\u0240\u0242")
        buf.write(u"\u0248\u024b\u024d\u0252\u0258\u025d\u0261\u0266\u0269")
        buf.write(u"\u026d\u0273\u0277\u027d\3\2\3\2")
        return buf.getvalue()


class PyNESTMLLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    T__9 = 10
    T__10 = 11
    T__11 = 12
    T__12 = 13
    T__13 = 14
    T__14 = 15
    T__15 = 16
    T__16 = 17
    T__17 = 18
    T__18 = 19
    T__19 = 20
    T__20 = 21
    T__21 = 22
    T__22 = 23
    T__23 = 24
    T__24 = 25
    T__25 = 26
    T__26 = 27
    T__27 = 28
    T__28 = 29
    T__29 = 30
    T__30 = 31
    T__31 = 32
    T__32 = 33
    T__33 = 34
    T__34 = 35
    T__35 = 36
    T__36 = 37
    T__37 = 38
    T__38 = 39
    T__39 = 40
    T__40 = 41
    T__41 = 42
    T__42 = 43
    T__43 = 44
    T__44 = 45
    T__45 = 46
    T__46 = 47
    T__47 = 48
    T__48 = 49
    T__49 = 50
    T__50 = 51
    T__51 = 52
    T__52 = 53
    T__53 = 54
    T__54 = 55
    T__55 = 56
    T__56 = 57
    T__57 = 58
    T__58 = 59
    T__59 = 60
    T__60 = 61
    T__61 = 62
    T__62 = 63
    T__63 = 64
    T__64 = 65
    T__65 = 66
    T__66 = 67
    T__67 = 68
    T__68 = 69
    SL_COMMENT = 70
    ML_COMMENT = 71
    NEWLINE = 72
    WS = 73
    LINE_ESCAPE = 74
    BLOCK_OPEN = 75
    BLOCK_CLOSE = 76
    BOOLEAN_LITERAL = 77
    STRING_LITERAL = 78
    NAME = 79
    INTEGER = 80
    FLOAT = 81

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'integer'", u"'real'", u"'string'", u"'boolean'", u"'void'", 
            u"'('", u"')'", u"'**'", u"'*'", u"'/'", u"'%'", u"'+'", u"'-'", 
            u"'not'", u"'?'", u"'inf'", u"'~'", u"'&'", u"'^'", u"'|'", 
            u"'<<'", u"'>>'", u"'<'", u"'<='", u"'=='", u"'!='", u"'<>'", 
            u"'>='", u"'>'", u"'and'", u"'or'", u"'''", u"','", u"'recordable'", 
            u"'function'", u"'='", u"';'", u"'shape'", u"'+='", u"'-='", 
            u"'*='", u"'/='", u"'['", u"']'", u"'[['", u"']]'", u"'return'", 
            u"'if'", u"'elif'", u"'else'", u"'for'", u"'in'", u"'...'", 
            u"'step'", u"'while'", u"'neuron'", u"'state'", u"'parameters'", 
            u"'internals'", u"'initial_values'", u"'update'", u"'equations'", 
            u"'input'", u"'<-'", u"'current'", u"'spike'", u"'inhibitory'", 
            u"'excitatory'", u"'output'", u"':'", u"'end'" ]

    symbolicNames = [ u"<INVALID>",
            u"SL_COMMENT", u"ML_COMMENT", u"NEWLINE", u"WS", u"LINE_ESCAPE", 
            u"BLOCK_OPEN", u"BLOCK_CLOSE", u"BOOLEAN_LITERAL", u"STRING_LITERAL", 
            u"NAME", u"INTEGER", u"FLOAT" ]

    ruleNames = [ u"T__0", u"T__1", u"T__2", u"T__3", u"T__4", u"T__5", 
                  u"T__6", u"T__7", u"T__8", u"T__9", u"T__10", u"T__11", 
                  u"T__12", u"T__13", u"T__14", u"T__15", u"T__16", u"T__17", 
                  u"T__18", u"T__19", u"T__20", u"T__21", u"T__22", u"T__23", 
                  u"T__24", u"T__25", u"T__26", u"T__27", u"T__28", u"T__29", 
                  u"T__30", u"T__31", u"T__32", u"T__33", u"T__34", u"T__35", 
                  u"T__36", u"T__37", u"T__38", u"T__39", u"T__40", u"T__41", 
                  u"T__42", u"T__43", u"T__44", u"T__45", u"T__46", u"T__47", 
                  u"T__48", u"T__49", u"T__50", u"T__51", u"T__52", u"T__53", 
                  u"T__54", u"T__55", u"T__56", u"T__57", u"T__58", u"T__59", 
                  u"T__60", u"T__61", u"T__62", u"T__63", u"T__64", u"T__65", 
                  u"T__66", u"T__67", u"T__68", u"SL_COMMENT", u"ML_COMMENT", 
                  u"NEWLINE", u"WS", u"LINE_ESCAPE", u"BLOCK_OPEN", u"BLOCK_CLOSE", 
                  u"BOOLEAN_LITERAL", u"STRING_LITERAL", u"NAME", u"INTEGER", 
                  u"NON_ZERO_INTEGER", u"FLOAT", u"POINT_FLOAT", u"EXPONENT_FLOAT", 
                  u"EXPONENT", u"FRACTION" ]

    grammarFileName = u"PyNESTML.g4"

    def __init__(self, input=None, output=sys.stdout):
        super(PyNESTMLLexer, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


