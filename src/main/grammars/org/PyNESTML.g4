/**
 *@author kperun
 *The grammar as well as the definition of tokens for PyNESTML.
*/
grammar PyNESTML;

/*************************************************************************
************************TOKENS DEFINTION**********************************/
/**
* The block start and finish tokens are used to indicate units of declaration.
* Example:
*   state:
*    ...
*   end
*/
BLOCK_START : ':' ;

BLOCK_END : 'end' ;

NEWLINE : ('\r' '\n' | '\r' | '\n' );

WS : (' ' | '\t')->channel(HIDDEN);

/**
* In order to reduce problems during parsing we use only a limited alphabet and the underscore.
* We do not allow strings which consist only of the underscore, since it could lead to undesired naming of variables.
* Example:
*  (1) __D_g_in
*/
STRING_LITERAL : ('_')* [a-zA-Z]* ('_')* [a-zA-Z]+;

/**
* Boolean values, i.e., true and false, should be handled as tokens in order to enable handling of lower
* and upper case definitions. Here, we allow both concepts, the python like syntax starting with upper case and
* the concept as currently used in NESTML with the lower case.
*/
BOOLEAN_TRUE_LITERAL : 'true' | 'True' ;
BOOLEAN_FALSE_LITERAL : 'false' | 'False' ;

/**
* Numeric literals. We allow integers as well as floats.
* Example:
*  (1) 1
*  (2) 3.14
*/

NUMERIC_LITERAL : [0-9]+ ('.' [0-9]+)?;

/**
* The infinity element is represented by the keyword inf. We allow lower or upper case keywords.
*/
INF_LITERAL : ('inf'|'Inf');


/*************************************************************************
************************GRAMMAR DEFINTION**********************************/
/**
* A variable consists of a name and an optional order.
* Example:
*   g_in''
*/
variable : var=STRING_LITERAL (order='\'')*;

/**
* An expression can be (1)simple, i.e. a numeric or alphabetical value with a signum, a (2)compound expression, i.e., consisting of two components
* combined by an operator, or an expression (3)encapsulated in brackets.
* Examples:
* (1) 10mV, g_in
* (2) V_m - 65mV, exp(10mV + V_m)
* (3) (2+2)**2
*/
expression : simpleExpression | compoundExpression | leftBracket='(' expression rightBracket=')';

/**
* Simple expression are those composed of a signum and a numeric value or reference. Moreover, it is allowed to used boolean literals here.
* Example:
* (1) -10mV
* TODO: we need to support units.
*/
simpleExpression : (unaryPlus='+' | unaryMinus='+' | unaryTilde='~')? (var=variable | num=NUMERIC_LITERAL | inf=INF_LITERAL ) | BOOLEAN_TRUE_LITERAL | BOOLEAN_FALSE_LITERAL;

/**
* A compound expression can be either:
* (1) a power expression, e.g., 2**2.
* (2) an arithmetic expression, e.g., 2+2, 2*2
* (3) a logical expression, e.g., x == y
* (4) a function call, e.g., myfunc(10ms)
*/
compoundExpression : arithmeticExpression | logicalExpression | functionCall;


/**
* An arithmetic expression is a combination of a two expression by an arithmetic operator.
* Example:
*  (1) 10mV + V_m*2
*  (2) 10mV**2
*/
arithmeticExpression : lhs=expression (timesOp='*'| divOp='/' | modOp='%' ) rhs=expression
                     | lhs=expression (plusOp='+' | minusOp='-') rhs=expression
                     | <assoc=right> base=expression powOp='**' exponent=expression
                     ;

/**
* Logic expressions are expressions which consisting of two sub-expression combined with a logic operator or a relation, the negation of a expression or the ternary
* operator.
* Examples:
*  (1) 10mV > V_m
*  (2) not r == 0
*  (3) V_m > 50mV? V_m = 50mV: V_m = V_m
*/
logicalExpression : logNot=('not'|'NOT') expr=expression
                  | lhs=expression (lt='<'|leq='<='|eq='=='|neq=('!='|'<>')|geq='>='|gt='>') rhs=expression
                  | lhs=expression logAnd=('and'|'AND') rhs=expression
                  | lhs=expression logOr=('or'|'OR') rhs=expression
                  | condition=expression '?' ifTrue=expression ':' ifNotTrue=expression
                  ;

/**
* Function calls represent calls to predefined (mathematical) or simulator specific functions.
* Example:
* (1) exp(10)
* (2) steps(10ms)
* (3) myFunc(10mV,1ms)
*/
functionCall : functionName=STRING_LITERAL '(' (args=parameter)? ')';

/**
* If a function calls contains any parameters, it should consist of at leas one parameter expression, and if subsequent parameters are there, then
* separated by a comma.
* Example:
* (1) (10mV)
* (2) (10mV,2mV)
*/
parameter: expression (',' expression)*;
