# Generated from pynestml/src/main/grammars/org/Tokens.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2")
        buf.write(u"\r\u00b5\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6")
        buf.write(u"\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4")
        buf.write(u"\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\3\2\3")
        buf.write(u"\2\7\2&\n\2\f\2\16\2)\13\2\3\2\3\2\3\2\3\2\7\2/\n\2\f")
        buf.write(u"\2\16\2\62\13\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\7\2;\n\2")
        buf.write(u"\f\2\16\2>\13\2\3\2\3\2\3\2\5\2C\n\2\3\2\3\2\3\3\3\3")
        buf.write(u"\3\3\5\3J\n\3\3\4\3\4\3\4\3\4\3\5\3\5\5\5R\n\5\3\5\3")
        buf.write(u"\5\3\5\3\5\3\6\3\6\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\3")
        buf.write(u"\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3")
        buf.write(u"\b\5\bp\n\b\3\t\3\t\5\tt\n\t\3\t\7\tw\n\t\f\t\16\tz\13")
        buf.write(u"\t\3\t\3\t\3\n\5\n\177\n\n\3\n\7\n\u0082\n\n\f\n\16\n")
        buf.write(u"\u0085\13\n\3\13\3\13\5\13\u0089\n\13\3\f\3\f\7\f\u008d")
        buf.write(u"\n\f\f\f\16\f\u0090\13\f\3\r\3\r\5\r\u0094\n\r\3\16\3")
        buf.write(u"\16\5\16\u0098\n\16\3\16\3\16\3\16\5\16\u009d\n\16\3")
        buf.write(u"\16\5\16\u00a0\n\16\3\17\3\17\5\17\u00a4\n\17\3\17\3")
        buf.write(u"\17\3\20\3\20\5\20\u00aa\n\20\3\20\3\20\5\20\u00ae\n")
        buf.write(u"\20\3\21\3\21\6\21\u00b2\n\21\r\21\16\21\u00b3\4\60<")
        buf.write(u"\2\22\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27")
        buf.write(u"\2\31\r\33\2\35\2\37\2!\2\3\2\n\4\2\f\f\17\17\4\2\13")
        buf.write(u"\13\"\"\6\2&&C\\aac|\7\2&&\62;C\\aac|\3\2\63;\3\2\62")
        buf.write(u";\4\2GGgg\4\2--//\2\u00c6\2\3\3\2\2\2\2\5\3\2\2\2\2\7")
        buf.write(u"\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3")
        buf.write(u"\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\31\3")
        buf.write(u"\2\2\2\3B\3\2\2\2\5I\3\2\2\2\7K\3\2\2\2\tO\3\2\2\2\13")
        buf.write(u"W\3\2\2\2\rY\3\2\2\2\17o\3\2\2\2\21q\3\2\2\2\23~\3\2")
        buf.write(u"\2\2\25\u0088\3\2\2\2\27\u008a\3\2\2\2\31\u0093\3\2\2")
        buf.write(u"\2\33\u009f\3\2\2\2\35\u00a3\3\2\2\2\37\u00a7\3\2\2\2")
        buf.write(u"!\u00af\3\2\2\2#\'\7%\2\2$&\n\2\2\2%$\3\2\2\2&)\3\2\2")
        buf.write(u"\2\'%\3\2\2\2\'(\3\2\2\2(C\3\2\2\2)\'\3\2\2\2*+\7\61")
        buf.write(u"\2\2+,\7,\2\2,\60\3\2\2\2-/\13\2\2\2.-\3\2\2\2/\62\3")
        buf.write(u"\2\2\2\60\61\3\2\2\2\60.\3\2\2\2\61\63\3\2\2\2\62\60")
        buf.write(u"\3\2\2\2\63\64\7,\2\2\64C\7\61\2\2\65\66\7$\2\2\66\67")
        buf.write(u"\7$\2\2\678\7$\2\28<\3\2\2\29;\13\2\2\2:9\3\2\2\2;>\3")
        buf.write(u"\2\2\2<=\3\2\2\2<:\3\2\2\2=?\3\2\2\2><\3\2\2\2?@\7$\2")
        buf.write(u"\2@A\7$\2\2AC\7$\2\2B#\3\2\2\2B*\3\2\2\2B\65\3\2\2\2")
        buf.write(u"CD\3\2\2\2DE\b\2\2\2E\4\3\2\2\2FG\7\17\2\2GJ\7\f\2\2")
        buf.write(u"HJ\t\2\2\2IF\3\2\2\2IH\3\2\2\2J\6\3\2\2\2KL\t\3\2\2L")
        buf.write(u"M\3\2\2\2MN\b\4\2\2N\b\3\2\2\2OQ\7^\2\2PR\7\17\2\2QP")
        buf.write(u"\3\2\2\2QR\3\2\2\2RS\3\2\2\2ST\7\f\2\2TU\3\2\2\2UV\b")
        buf.write(u"\5\2\2V\n\3\2\2\2WX\7<\2\2X\f\3\2\2\2YZ\7g\2\2Z[\7p\2")
        buf.write(u"\2[\\\7f\2\2\\\16\3\2\2\2]^\7v\2\2^_\7t\2\2_`\7w\2\2")
        buf.write(u"`p\7g\2\2ab\7V\2\2bc\7t\2\2cd\7w\2\2dp\7g\2\2ef\7h\2")
        buf.write(u"\2fg\7c\2\2gh\7n\2\2hi\7u\2\2ip\7g\2\2jk\7H\2\2kl\7c")
        buf.write(u"\2\2lm\7n\2\2mn\7u\2\2np\7g\2\2o]\3\2\2\2oa\3\2\2\2o")
        buf.write(u"e\3\2\2\2oj\3\2\2\2p\20\3\2\2\2qs\7$\2\2rt\t\4\2\2sr")
        buf.write(u"\3\2\2\2tx\3\2\2\2uw\t\5\2\2vu\3\2\2\2wz\3\2\2\2xv\3")
        buf.write(u"\2\2\2xy\3\2\2\2y{\3\2\2\2zx\3\2\2\2{|\7$\2\2|\22\3\2")
        buf.write(u"\2\2}\177\t\4\2\2~}\3\2\2\2\177\u0083\3\2\2\2\u0080\u0082")
        buf.write(u"\t\5\2\2\u0081\u0080\3\2\2\2\u0082\u0085\3\2\2\2\u0083")
        buf.write(u"\u0081\3\2\2\2\u0083\u0084\3\2\2\2\u0084\24\3\2\2\2\u0085")
        buf.write(u"\u0083\3\2\2\2\u0086\u0089\5\27\f\2\u0087\u0089\7\62")
        buf.write(u"\2\2\u0088\u0086\3\2\2\2\u0088\u0087\3\2\2\2\u0089\26")
        buf.write(u"\3\2\2\2\u008a\u008e\t\6\2\2\u008b\u008d\t\7\2\2\u008c")
        buf.write(u"\u008b\3\2\2\2\u008d\u0090\3\2\2\2\u008e\u008c\3\2\2")
        buf.write(u"\2\u008e\u008f\3\2\2\2\u008f\30\3\2\2\2\u0090\u008e\3")
        buf.write(u"\2\2\2\u0091\u0094\5\33\16\2\u0092\u0094\5\35\17\2\u0093")
        buf.write(u"\u0091\3\2\2\2\u0093\u0092\3\2\2\2\u0094\32\3\2\2\2\u0095")
        buf.write(u"\u0098\5\27\f\2\u0096\u0098\7\62\2\2\u0097\u0095\3\2")
        buf.write(u"\2\2\u0097\u0096\3\2\2\2\u0097\u0098\3\2\2\2\u0098\u0099")
        buf.write(u"\3\2\2\2\u0099\u00a0\5!\21\2\u009a\u009d\5\27\f\2\u009b")
        buf.write(u"\u009d\7\62\2\2\u009c\u009a\3\2\2\2\u009c\u009b\3\2\2")
        buf.write(u"\2\u009d\u009e\3\2\2\2\u009e\u00a0\7\60\2\2\u009f\u0097")
        buf.write(u"\3\2\2\2\u009f\u009c\3\2\2\2\u00a0\34\3\2\2\2\u00a1\u00a4")
        buf.write(u"\5\27\f\2\u00a2\u00a4\5\33\16\2\u00a3\u00a1\3\2\2\2\u00a3")
        buf.write(u"\u00a2\3\2\2\2\u00a4\u00a5\3\2\2\2\u00a5\u00a6\5\37\20")
        buf.write(u"\2\u00a6\36\3\2\2\2\u00a7\u00a9\t\b\2\2\u00a8\u00aa\t")
        buf.write(u"\t\2\2\u00a9\u00a8\3\2\2\2\u00a9\u00aa\3\2\2\2\u00aa")
        buf.write(u"\u00ad\3\2\2\2\u00ab\u00ae\5\27\f\2\u00ac\u00ae\7\62")
        buf.write(u"\2\2\u00ad\u00ab\3\2\2\2\u00ad\u00ac\3\2\2\2\u00ae \3")
        buf.write(u"\2\2\2\u00af\u00b1\7\60\2\2\u00b0\u00b2\t\7\2\2\u00b1")
        buf.write(u"\u00b0\3\2\2\2\u00b2\u00b3\3\2\2\2\u00b3\u00b1\3\2\2")
        buf.write(u"\2\u00b3\u00b4\3\2\2\2\u00b4\"\3\2\2\2\32\2\'\60<BIQ")
        buf.write(u"osvx~\u0081\u0083\u0088\u008e\u0093\u0097\u009c\u009f")
        buf.write(u"\u00a3\u00a9\u00ad\u00b3\3\2\3\2")
        return buf.getvalue()


class Tokens(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    SL_COMMENT = 1
    NEWLINE = 2
    WS = 3
    LINE_ESCAPE = 4
    BLOCK_OPEN = 5
    BLOCK_CLOSE = 6
    BOOLEAN_LITERAL = 7
    STRING_LITERAL = 8
    NAME = 9
    INTEGER = 10
    FLOAT = 11

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"':'", u"'end'" ]

    symbolicNames = [ u"<INVALID>",
            u"SL_COMMENT", u"NEWLINE", u"WS", u"LINE_ESCAPE", u"BLOCK_OPEN", 
            u"BLOCK_CLOSE", u"BOOLEAN_LITERAL", u"STRING_LITERAL", u"NAME", 
            u"INTEGER", u"FLOAT" ]

    ruleNames = [ u"SL_COMMENT", u"NEWLINE", u"WS", u"LINE_ESCAPE", u"BLOCK_OPEN", 
                  u"BLOCK_CLOSE", u"BOOLEAN_LITERAL", u"STRING_LITERAL", 
                  u"NAME", u"INTEGER", u"NON_ZERO_INTEGER", u"FLOAT", u"POINT_FLOAT", 
                  u"EXPONENT_FLOAT", u"EXPONENT", u"FRACTION" ]

    grammarFileName = u"Tokens.g4"

    def __init__(self, input=None, output=sys.stdout):
        super(Tokens, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


