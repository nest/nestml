/*
 *  Tokens.g4
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

lexer grammar Tokens;

  @lexer::members {
    HIDDEN = 1
    COMMENT = 2
    NEW_LINE = 3
  }


  channels {COMMENT}

  SL_COMMENT: ('#' (~('\n' |'\r' ))*) -> channel(2);

  ML_COMMENT : ('/*' .*? '*/' | '"""' .*? '"""')-> channel(2);

  NEWLINE : ('\r' '\n' | '\r' | '\n' ) -> channel(3);

  WS : (' ' | '\t')->channel(1);

  // this token enables an expression that stretches over multiple lines. The first line ends with a `\` character
  LINE_ESCAPE : '\\' '\r'? '\n'->channel(1);

  BLOCK_OPEN : ':';

  BLOCK_CLOSE : 'end';

  /**
  * Boolean values, i.e., true and false, should be handled as tokens in order to enable handling of lower
  * and upper case definitions. Here, we allow both concepts, the python like syntax starting with upper case and
  * the concept as currently used in NESTML with the lower case.
  */
  BOOLEAN_LITERAL : 'true' | 'True' | 'false' | 'False' ;

  /**
  * String literals are always enclosed in "...".
  */

  STRING_LITERAL : '"' ( [a-zA-Z] | '_' | '$' )( [a-zA-Z] | '_' | [0-9] | '$' )* '"';

  NAME : ( [a-zA-Z] | '_' | '$' )( [a-zA-Z] | '_' | [0-9] | '$' )*;

  /**
  * Numeric literals. We allow integers as well as floats. Moreover, we ensure that values are either == 0 or
  * do not start with 0, e.g., 01221.012, where the leading 0 does not make sense.
  * Examples:
  *  (1) 1 -> integer
  *  (2) 3.14 -> float
  *  (3) 10E10 -> float with exponent
  */
  INTEGER : NON_ZERO_INTEGER
          | '0';

  DIFFERENTIAL_ORDER : '\'';

  fragment NON_ZERO_INTEGER : [1-9][0-9]*;

  /**
  * The following declaration originates from Antrl4 Python Grammar definition as distributed under the MIT license.
  * link: https://github.com/antlr/grammars-v4/blob/master/python3/Python3.g4
  */

  /*
  * A float can be a point float, e.g., 10.05 or 0.1, or an exponent float, e.g. 10E10.
  */
  FLOAT : POINT_FLOAT | EXPONENT_FLOAT;

  fragment POINT_FLOAT : (NON_ZERO_INTEGER |'0')? FRACTION
                       | (NON_ZERO_INTEGER |'0') '.'
                       ;

  fragment EXPONENT_FLOAT: ( NON_ZERO_INTEGER | POINT_FLOAT ) EXPONENT ;

  /**
  * The exponent is introduced by e or E, the signum and an integer.
  */
  fragment EXPONENT: [eE] [+-]? (NON_ZERO_INTEGER |'0');

  fragment FRACTION: '.' [0-9]+;
