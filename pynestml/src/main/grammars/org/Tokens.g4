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
 * @author dplotnikov, kperun
 */

lexer grammar Tokens;


  SL_COMMENT : ('#' (~('\n' |'\r' ))*|
               '/*' .*? '*/' | '"""' .*? '"""')
               -> channel(HIDDEN)
             ;

  NEWLINE : ('\r' '\n' | '\r' | '\n' );

  WS : (' ' | '\t')->channel(HIDDEN);

  // this token enables an expression that stretches over multiple lines. The first line end with a `\` character
  LINE_ESCAPE : '\\' '\r'? '\n'->channel(HIDDEN);

  BLOCK_OPEN : ':';

  BLOCK_CLOSE : 'end';

  /**
  * Boolean values, i.e., true and false, should be handled as tokens in order to enable handling of lower
  * and upper case definitions. Here, we allow both concepts, the python like syntax starting with upper case and
  * the concept as currently used in NESTML with the lower case.
  */
  BOOLEAN_LITERAL : 'true' | 'True' | 'false' | 'False' ;

  /**
  * Numeric literals. We allow integers as well as floats. Moreover, we ensure that values are either == 0 or
  * do not start with 0, e.g., 01221.012, where the leading 0 does not make sense.
  * Examples:
  *  (1) 1
  *  (2) 3.14
  */
  NUMERIC_LITERAL :  ([1-9][0-9]* | '0' ) ('.' [0-9]*)?;

  NAME : ( [a-zA-Z] | '_' | '$' )( [a-zA-Z] | '_' | [0-9] | '$' )*;
