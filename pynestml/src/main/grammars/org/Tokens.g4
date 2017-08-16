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
