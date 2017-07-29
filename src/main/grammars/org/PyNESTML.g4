/**
 *@author kperun
 *The grammar as well as the definition of tokens for PyNESTML.
*/
grammar PyNESTML;

/*************************************************************************
************************TOKENS DEFINTION**********************************/

/**
* The block start and finish tokens are used to indicate units of declaration.
*/
BLOCK_START : ':' ;

BLOCK_END : 'end' ;

NEWLINE = ('\r' '\n' | '\r' | '\n' );

WS = (' ' | '\t')->channel(HIDDEN);

/**
* In order to reduce problems during parsing we use only a limited alphabet and the underscore.
* TODO: here we should no allow literals consisting only of _ .
*/
STRING_LITERAL : [a-zA-Z\\_];

/**
* Boolean values, i.e., true and false, should be handled as tokens in order to enable handling of lower
* and upper case definitions.
*/
BOOLEAN_TRUE_LITERAL : 'true' | 'TRUE' ;
BOOLEAN_FALSE_LITERAL : 'false' | 'FALSE' ;


/**
* Numeric literals. We allow integers as well as floats.
* Example:
*   1, 3.14, ....
*/

NUMERIC_LITERAL : [0-9]+(\.[0-9]+)?;

/*
* The infinity element is represented by the keyword inf. We allow lower or upper case keywords.
*/
INF_LITERAL : ("inf"|"INF");


/*************************************************************************
************************GRAMMAR DEFINTION**********************************/
/**
* A variable consists of a name and an optional order.
* Example:
*   g_in''
*/
Variable : var=STRING_LITERAL (order='\'')*;

/**
* An expression can be (1)simple, i.e. a numeric or alphabetical value with a signum, a (2)compound expression, i.e., consisting of two components
* combined by an operator, or an expression (3)encapsulated in brackets.
* Examples:
* (1) 10mV, g_in
* (2) V_m - 65mV, exp(10mV + V_m)
* (3) (2+2)**2
*/
Expression : SimpleExpression | CompoundExpression | leftBracket='(' Expression leftBracket='(';

/**
* Simple expression are those composed of a signum and a numeric value or reference. Moreover, it is allowed to used boolean literals here.
* TODO: What about the unary tilde?
*
*/
SimpleExpression : (unaryPlus='+' | unaryMinus='+')? (var=Variable | num=NUMERIC_LITERAL | inf=INF_LITERAL ) | BOOLEAN_TRUE_LITERAL | BOOLEAN_FALSE_LITERAL;

/**
* A compound expression can be either:
* - a power expression, e.g., 2**2.
* - a point expression (times,div,modulo), e.g., 2*2.
* - a TODOExpression (plus,minus), e.g., 2-2
*/
CompoundExpression : PowerExpression | PointExpression | TODOExpression | LogicalExpression | FunctionCall;

/**
* A power expression consisting of a base and the corresponding exponent.
*/

PowerExpression : <assorc=right> base=Expression "**" exponent=Expression;

/**
* An arithmetic expression is a combination of a two expression by an arithmetic operator.
* Example:
*   10mV + V_m*2
*/
ArithmeticExpression : lhs=Expression (timesOp='*'|divOp='/' | modOp='%' | plusOp='+' | minusOp='-') rhs=Expression;

/**
* Logic expressions are expressions which consisting of two sub-expression combined with a logic operator or a relation, the negation of a expression or the ternary
* operator.
* Examples:
*   10mV > V_m, not r == 0, V_m > 50mV? V_m = 50mV: V_m = V_m
*/
LogicalExpression : lhs=Expression (lt="<"|leq="<="|eq="=="|neq=("!="|"<>")|geq=">="|gt=">") rhs=Expression
                  | logNot=("not"|"NOT") expr=Expression
                  | lhs=Expression logAnd=("and"|"AND") rhs=Expression
                  | lhs=Expression logOr=("or"|"OR") rhs=Expression
                  | condition=Expression '?' ifTrue=Expression ':' ifNotTrue=Expression
                  ;

/**
* Function calls represent calls to predefined (mathematical) or simulator specific functions.
* Example:
*  exp(10), steps(10ms), myFunc(10mV,1ms)
*/
FunctionCall : functionName=STRING_LITERAL '(' (args=Parameter)? ')';

/**
* If a function calls contains any parameters, it should consist of at leas one parameter expression, and if subsequent parameters are there, then
* separated by a comma.
* Example:
*   (10mV)
*   (10mV,2mV)
*/
Parameter: Expression (',' Expression)*;
