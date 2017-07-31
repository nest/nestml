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
* Numeric literals. We allow integers as well as floats. Moreover, we ensure that values are either == 0 or
* do not start with 0, e.g., 01221.012, where the leading 0 does not make sense.
* Examples:
*  (1) 1
*  (2) 3.14
*/
NUMERIC_LITERAL :  ( [1-9][0-9]* | '0' ) ('.' [0-9]+)?;

/**
* An integer literal as often required for the exponent of a unit.
* Examples:
*  (1) 42
*/
INT_LITERAL : ([1-9][0-9]* | '0' );


/**
* The infinity element is represented by the keyword inf. We allow lower or upper case keywords.
*/
INF_LITERAL : ('inf');

/**************************************************************************
************************GRAMMAR DEFINTION**********************************
/**************************************************************************
***********************COMMENT LANGUAGE DEFINTION*************************/

/**
* Multi-line comments are encapsulated in Java Style comments tags or
* by means of Python multi-line comment tags (""" ... """). Single line comments are introduced by a hashtag #.
* Comments should be processed in the parser part in order to avoid problems with "evil characters".and reverse matching.
* TODO:Revise
* Examples:
*  (1) /* comment */
/* (2) """ comment """
*  (3) # comment
*/
comment : '#' (~(NEWLINE))* NEWLINE  /*everything which is not a new line */
        | '/*' (~('*/'))*  '*/'      /*everything which is not a end of comment in Java style */
        | '"""' (~('""""'))* '"""'   /*everything which is not a end of comment in Python style */
        ;

/**************************************************************************
**********************EXPRESSION LANGUAGE**********************************/
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
expression : simpleExpression | compoundExpression | leftParenthesis='(' expression rightParenthesis=')';

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
logicalExpression : logNot=('not') expr=expression
                  | lhs=expression (lt='<'|leq='<='|eq='=='|neq=('!='|'<>')|geq='>='|gt='>') rhs=expression
                  | lhs=expression logAnd=('and') rhs=expression
                  | lhs=expression logOr=('or') rhs=expression
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

/*******************************************************************************
****************************DATA-TYPE LANGUAGE DEFINTION************************/
/**
* Data-type Language: A defined element can have either a primitive data type or a SI unit type.
* Example:
*  (1) integer
*  (2) mV
*/
dataType : primitiveType | unitType ;

/**
* Primitive Data-types represent data types which are integrated in the language directly.
* Example:
*  (1) boolean
*  (2) void
*/
primitiveType : 'boolean'
              | 'void'
              | 'integer'
              | 'real'
              | 'string'
              ;

/**
* Unit types are either plain text definitions of physical units, e.g., mV, or complex, compound
* physical units, e.g., (mV/ms)
* Examples:
*  (1) mV
*  (2) mS/ms
*/
unitType : leftParenthesis='(' unitType rightParenthesis=')'
         | base=unitType powOp='**' exponent=INT_LITERAL
         | lhs=unitType (timesOp='*' | divOp='/') rhs=unitType
         | unitlessLhs=INT_LITERAL divOp='/' rhs=unitType
         | unit=STRING_LITERAL
         ;

/*******************************************************************************
**********ORDINARY DIFFERENTIAL EQUATION LANGUAGE DEFINTION*********************/

odeDeclaration : (odeFunction | odeShape | odeEquation | NEWLINE)*;


/**
* Declaration of a ODE functions. Optionally, it can be set as recordable. It has to be introduced by the
* keyword 'function', a name and the data-type.
* Example:
*  (1) function V_init mV = ....
*/
odeFunction : (recordable='recordable')? 'function' lhs=STRING_LITERAL dataType '=' expression ;

/**
* Equations consist of a right-hand side and a left-hand side combined by means of the equality symbol.
* Example:
*  (1) g_in' = g_in'' + V_in
*/
odeEquation : lhs=variable '=' rhs=expression ;

/**
* ODE shapes are introduced by the keyword 'shape' and the name of the variable to which they belong. The
* right-hand side defined the behavior.
* Example:
*  (1) shape f_in = .....
*/
odeShape : 'shape' lhs=variable '=' rhs=expression ;

/*********************************************************************
********************FUNCTIONAL LANGUAGE DEFINTION*********************/

block : (statement | NEWLINE)* ;

statement : simpleStatement | compoundStatement ;

simpleStatement : declaration | assignment | functionCall | return ;

/**
* A declaration can be a function (i.e., "alias") and recordable. Moreover, multi-declarations separated by comma are allowed. The left-hand side
* is optional, but can be provided, as well as a comment, a array index assignment as well as a invariant.
* Examples:
*  (1) recordable function g_reset = g_in - 50mV
*/
declaration : ('recordable')? ('function')?
              lhs=(Variable (',' Variable)? ) dataType
              ('[' index=STRING_LITERAL ']')?
              ('=' rhs=expression)? comment?
              ('[[' invariant=expression ']]')?
              ;

/**
* Assignments are used to assign values to variables. We support normal assignments as well as short-hand assignments for both, arithmetic as well
* as bit operations.
* Examples:
*  (1) g_in += V_m
*  (2) b_in <<= 2
*/
assignment : lhs=variable '=' rhs=expression
           | lhs=variable (sumAssign='+=' | difAssign='-=' | proAssign='*=' | divAssign='/=' | modAssign='%=' | powAssign='**=') rhs=expression /*arithmetic compound assignments*/
           | lhs=variable (bslAssign='<<' | bsrAssign='>>' | boAssign= '|' | baAssign='&' | bxAssign='^') rhs=expression /*bit operator compound assignments*/
           ;

/**
* Return statements as used to indicated what is returned by the procedure.
* Examples:
*  (1) return V_m + 10mV
*/
return : 'return' (returnValue=expression)?;

/**
* Compound statements are those which initiate a new block of statements, i.e., if, while or for blocks.
* (1) while V_m > 10mV:
*     ...
*     end
*/
compoundStatement : (ifBlock | whileBlock | forBlock) BLOCK_END;

/**
* If-blocks consist of a mandatory if condition and a set of corresponding expression, while else-if and else conditions as well
* as the corresponding blocks are optional.
* Example:
*  (1) if V_m > 10mV:
*       ...
*      elif V_m == 0mV:
*       ...
*      end
*/
ifBlock : 'if' ifCond=expression BLOCK_START ifBlock=block
         ('elif' elifCond=expression BLOCK_START elifBlock=block)*
         ('else' BLOCK_START elseBlock=block)?;

/**
* While-blocks consist of a mandatory conditions and a block containing a set of statements.
* Examples:
*  (1) while V_m > 10mV:
*       ...
*      end
*/
whileBlock : 'while' whileCond=expression BLOCK_START whileBlock=block;

/**
* For-blocks consist of a iteration-variable and a range over which is iterated. An optional step length can be proved.
* Examples:
*  (1) for i in range(0,10,1):
*       ...
*      end
*/
forBlock : 'for' item=STRING_LITERAL 'in' 'range' '(' from=expression ',' to=expression ',' (step=( ('+'|'-') NUMERIC_LITERAL)) BLOCK_START block;

/*******************************************************************************
*******************NEURON DECLARATION LANGUAGE DEFINTION************************/
/**
* First we define the entry point into the parsing process.
*/
nestmlNeuronCollection : (neuron | NEWLINE )* EOF;
