/*
 *  PyNestML.g4
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

parser grammar PyNestMLParser;

  options { tokenVocab = PyNestMLLexer; }


  /*********************************************************************************************************************
  * Units-Language
  *********************************************************************************************************************/

  /**
    ASTDatatype. Represents predefined data types and gives a possibility to use an unit
    data type.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI data type
  */
  dataType : isInt=INTEGER_KEYWORD
           | isReal=REAL_KEYWORD
           | isString=STRING_KEYWORD
           | isBool=BOOLEAN_KEYWORD
           | isVoid=VOID_KEYWORD
           | unit=unitType;
  /**
    ASTUnitType. Represents an unit data type. It can be a plain data type as 'mV' or a
    complex data type as 'mV/s'
  */
  unitType : leftParentheses=LEFT_PAREN compoundUnit=unitType rightParentheses=RIGHT_PAREN
           | base=unitType powOp=STAR_STAR exponent=unitTypeExponent
           | left=unitType (timesOp=STAR | divOp=FORWARD_SLASH) right=unitType
           | unitlessLiteral=UNSIGNED_INTEGER divOp=FORWARD_SLASH right=unitType
           | unit=NAME;

  unitTypeExponent : ( PLUS | MINUS )? UNSIGNED_INTEGER;


  /*********************************************************************************************************************
  * Expressions-Language
  *********************************************************************************************************************/

  /**
   ASTExpression, i.e., several subexpressions combined by one or more operators,
   e.g., 10mV + V_m - (V_reset * 2)/ms, or a simple expression, e.g. 10mV.
  */
  expression : leftParentheses=LEFT_PAREN term=expression rightParentheses=RIGHT_PAREN
         | <assoc=right> left=expression powOp=STAR_STAR right=expression
         | unaryOperator term=expression
         | left=expression (timesOp=STAR | divOp=FORWARD_SLASH | moduloOp=PERCENT) right=expression
         | left=expression (plusOp=PLUS | minusOp=MINUS) right=expression
         | left=expression bitOperator right=expression
         | left=expression comparisonOperator right=expression
         | logicalNot=NOT_KEYWORD term=expression
         | left=expression logicalOperator right=expression
         | condition=expression QUESTION ifTrue=expression COLON ifNot=expression
         | simpleExpression
         ;

  /**
    ASTSimpleExpression, consisting of a single element without combining operator, e.g.,
    10mV, inf, V_m.
    @attribute functionCall: A simple function call, e.g., myFunc(a,b)
    @attribute BOOLEAN_LITERAL: A single boolean literal, e.g., True.
    @attribute INTEGER: A integer number, e.g., 10.
    @attribute FLOAT: A float number, e.g., 10.01.
    @attribute variable: A optional variable representing the unit, e.g., ms, OR a single variable representing a reference, e.g. V_m.
    @attribute isInf: True iff, this expression shall represent the value infinity.
  */
  simpleExpression : functionCall
                   | BOOLEAN_LITERAL // true & false;
                   | (UNSIGNED_INTEGER | FLOAT) (variable)?
                   | string=STRING_LITERAL
                   | isInf=INF_KEYWORD
                   | variable;

  unaryOperator : (unaryPlus=PLUS | unaryMinus=MINUS | unaryTilde=TILDE);

  bitOperator : (bitAnd=AMPERSAND | bitXor=CARET | bitOr=PIPE | bitShiftLeft=LEFT_LEFT_ANGLE | bitShiftRight=RIGHT_RIGHT_ANGLE);

  comparisonOperator : (lt=LEFT_ANGLE | le=LEFT_ANGLE_EQUALS | eq=EQUALS_EQUALS | ne=EXCLAMATION_EQUALS | ne2=LEFT_ANGLE_RIGHT_ANGLE | ge=RIGHT_ANGLE_EQUALS | gt=RIGHT_ANGLE);

  logicalOperator : (logicalAnd=AND_KEYWORD | logicalOr=OR_KEYWORD );

  /**
    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    @attribute name: The name of the variable without the differential order, e.g. V_m
    @attribute vectorParameter: An optional array parameter, e.g., 'tau_syn ms[n_receptors]'.
    @attribute differentialOrder: The corresponding differential order, e.g. 2
  */
  variable : name=NAME
  (LEFT_SQUARE_BRACKET vectorParameter=expression RIGHT_SQUARE_BRACKET)?
  (DIFFERENTIAL_ORDER)*
  (FULLSTOP attribute=variable)?;

  /**
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute calleeName: The (qualified) name of the functions
    @attribute args: Comma separated list of expressions representing parameters.
  */
  functionCall : calleeName=NAME LEFT_PAREN (expression (COMMA expression)*)? RIGHT_PAREN;

  /*********************************************************************************************************************
  * Equations-Language
  *********************************************************************************************************************/

  inlineExpression : (recordable=RECORDABLE_KEYWORD)? INLINE_KEYWORD variableName=NAME dataType EQUALS expression (SEMICOLON)? decorator=anyDecorator* NEWLINE;

  odeEquation : lhs=variable EQUALS rhs=expression (SEMICOLON)? decorator=anyDecorator* NEWLINE;

  kernel : KERNEL_KEYWORD variable EQUALS expression (KERNEL_JOINING variable EQUALS expression)* SEMICOLON? NEWLINE;

  /*********************************************************************************************************************
  * Procedural-Language
  *********************************************************************************************************************/

  block : NEWLINE INDENT stmt+ DEDENT;

  stmt : smallStmt | compoundStmt;

  compoundStmt : ifStmt
               | forStmt
               | whileStmt;

  smallStmt : (assignment
            | functionCall
            | declaration
            | returnStmt) NEWLINE;

  assignment : lhs_variable=variable
                (directAssignment=EQUALS |
                 compoundSum=PLUS_EQUALS |
                 compoundMinus=MINUS_EQUALS |
                 compoundProduct=STAR_EQUALS |
                 compoundQuotient=FORWARD_SLASH_EQUALS)
               expression;

  /** ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
   'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
    @attribute isRecordable: Is true iff. declaration is recordable.
    @attribute isInlineExpression: Is true iff. declaration is an inline expression.
    @attribute variable: List with variables.
    @attribute datatype: Obligatory data type, e.g., 'real' or 'mV/s'.
    @attribute rhs: An optional initial expression, e.g., 'a real = 10+10'
    @attribute invariant: A single, optional invariant expression, e.g., '[a < 21]'
   */
  declaration :
    (isRecordable=RECORDABLE_KEYWORD)? (isInlineExpression=INLINE_KEYWORD)?
    variable (COMMA variable)*
    dataType
    ( EQUALS rhs = expression)?
    (LEFT_LEFT_SQUARE invariant=expression RIGHT_RIGHT_SQUARE)?
    decorator=anyDecorator*;

  declaration_newline: declaration NEWLINE;

  /** ...
  */
  anyDecorator : DECORATOR_HOMOGENEOUS | DECORATOR_HETEROGENEOUS | AT namespaceDecoratorNamespace DOUBLE_COLON namespaceDecoratorName;

  /**
    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    @attribute name: The name of the variable without the differential order, e.g. V_m
    @attribute differentialOrder: The corresponding differential order, e.g. 2
  */
  namespaceDecoratorNamespace : name=NAME;
  namespaceDecoratorName : name=NAME;

  /** ASTReturnStmt Models the return statement in a function.
    @expression An optional return expression, e.g., return tempVar
   */
  returnStmt : RETURN_KEYWORD expression?;

  ifStmt : ifClause
            elifClause*
            (elseClause)?;

  ifClause : IF_KEYWORD expression COLON block;

  elifClause : ELIF_KEYWORD expression COLON block;

  elseClause : ELSE_KEYWORD COLON block;

  forStmt : FOR_KEYWORD var=NAME IN_KEYWORD start_from=expression ELLIPSIS end_at=expression STEP_KEYWORD
            (negative=MINUS?) (UNSIGNED_INTEGER | FLOAT)
            COLON
             block;

  whileStmt : WHILE_KEYWORD expression COLON block;

  /*********************************************************************************************************************
  * NestML: language root element
  *********************************************************************************************************************/

  /** ASTNestMLCompilationUnit represents a collection of models.
    @attribute model: A list of processed models.
  */
  nestMLCompilationUnit: ( model | NEWLINE )+ EOF;

/*********************************************************************************************************************
  * NestML model and model blocks
  *********************************************************************************************************************/

  /** ASTModel Represents a single dynamical system model, such as a neuron or a synapse.
    @attribute Name:    The name of the model, e.g., ht_neuron.
    @attribute body:    The body of the model consisting of several sub-blocks.
  */
  model : MODEL_KEYWORD NAME modelBody;

  /** ASTBody The body of the model, e.g. internal, state, parameter...
    @attribute blockWithVariables: A single block of variables, e.g. the state block.
    @attribute equationsBlock: A block of ode declarations.
    @attribute inputBlock: A block of input port declarations.
    @attribute outputBlock: A block of output declarations.
    @attribute updateBlock: A single update block containing the dynamic behavior.
    @attribute function: A block declaring a user-defined function.
  */
  modelBody: COLON
         NEWLINE INDENT ( blockWithVariables | equationsBlock | inputBlock | outputBlock | function | onReceiveBlock | onConditionBlock | updateBlock )+ DEDENT;

  /** ASTOnReceiveBlock
     @attribute block implementation of the dynamics
   */
  onReceiveBlock: ON_RECEIVE_KEYWORD LEFT_PAREN inputPortVariable=variable (COMMA constParameter)* RIGHT_PAREN COLON
                block;

  /** ASTOnConditionBlock
     @attribute block implementation of the dynamics
   */
  onConditionBlock: ON_CONDITION_KEYWORD LEFT_PAREN condition=expression (COMMA constParameter)* RIGHT_PAREN COLON
                block;

  /** ASTBlockWithVariables Represent a block with variables and constants, e.g.:
    state:
        y0, y1, y2, y3 mV [y1 > 0; y2 > 0]

    @attribute state: True iff the varblock is a state.
    @attribute parameters:  True iff the varblock is a parameters block.
    @attribute internals: True iff the varblock is a state internals block.
    @attribute declaration: A list of corresponding declarations.
  */
  blockWithVariables:
    blockType=(STATE_KEYWORD | PARAMETERS_KEYWORD | INTERNALS_KEYWORD)
    COLON
      NEWLINE INDENT declaration_newline+ DEDENT;

  /** ASTUpdateBlock The definition of a block where the dynamical behavior of the neuron is stated:
      update:
          if r == 0: # not refractory
              integrate(V)
     @attribute block Implementation of the dynamics.
   */
  updateBlock: UPDATE_KEYWORD COLON
                block;

  /** ASTEquationsBlock A block declaring equations and inline expressions.
     @attribute inlineExpression: A single inline expression, e.g., inline V_m mV = ...
     @attribute odeEquation: A single ode equation statement, e.g., V_m' = ...
   */
  equationsBlock: EQUATIONS_KEYWORD COLON
                   NEWLINE INDENT ( inlineExpression | odeEquation | kernel )+ DEDENT;

  /** ASTInputBlock represents a single input block, e.g.:
    input:
        spike_in <- spike
        current_in pA <- continuous
    @attribute inputPort: A list of input ports.
  */
  inputBlock: INPUT_KEYWORD COLON
              NEWLINE INDENT (spikeInputPort | continuousInputPort)+ DEDENT;

  /** ASTInputPort represents a single input port, e.g.:
      spike_in[3] <- spike
      I_stim[3] pA <- continuous
    @attribute name: The name of the input port.
    @attribute sizeParameter: Optional size parameter for model with multiple input ports.
    @attribute datatype: Optional data type of the port.
    @attribute isSpike: Indicates that this input port accepts spikes.
    @attribute isContinuous: Indicates that this input port accepts continuous-time input.
  */
  spikeInputPort:
    name=NAME
    (LEFT_SQUARE_BRACKET sizeParameter=expression RIGHT_SQUARE_BRACKET)?
    LEFT_ANGLE_MINUS SPIKE_KEYWORD (LEFT_PAREN (parameter (COMMA parameter)*)? RIGHT_PAREN)? NEWLINE;

  continuousInputPort:
    name = NAME
    (LEFT_SQUARE_BRACKET sizeParameter=expression RIGHT_SQUARE_BRACKET)?
    dataType
    LEFT_ANGLE_MINUS CONTINUOUS_KEYWORD NEWLINE;


  /** ASTOutputBlock Represents the output block of the neuron, i.e., declarations of output ports:
        output:
            spike
      @attribute isSpike: true if and only if the neuron has a spike output.
      @attribute isContinuous: true if and only if the neuron has a continuous-time output.
    */
  outputBlock: OUTPUT_KEYWORD COLON
               NEWLINE INDENT (isSpike=SPIKE_KEYWORD | isContinuous=CONTINUOUS_KEYWORD)
               (LEFT_PAREN (attribute=parameter (COMMA attribute=parameter)*)? RIGHT_PAREN)?
               NEWLINE DEDENT;

  /** ASTFunction A single declaration of a user-defined function definition:
      function set_V_m(v mV):
          y3 = v - E_L
    @attribute name: The name of the function.
    @attribute parameters: List with function parameters.
    @attribute returnType: An arbitrary return type, e.g. string or mV.
    @attribute block: Implementation of the function.
  */
  function: FUNCTION_KEYWORD NAME LEFT_PAREN (parameter (COMMA parameter)*)? RIGHT_PAREN (returnType=dataType)?
           COLON
             block
           ;

  /** ASTParameter represents a single parameter consisting of a name and the corresponding
      data type, e.g. T_in ms
    @attribute name: The name of the parameter.
    @attribute dataType: The corresponding data type.
  */
  parameter : NAME dataType;

  /** ASTConstParameter represents a single parameter consisting of a name and a literal default value, e.g. "foo=42".
    @attribute name: The name of the parameter.
    @attribute value: The corresponding default value.
  */
  constParameter : name=NAME EQUALS value=(BOOLEAN_LITERAL
                                      | UNSIGNED_INTEGER
                                      | FLOAT
                                      | STRING_LITERAL
                                      | INF_KEYWORD);
