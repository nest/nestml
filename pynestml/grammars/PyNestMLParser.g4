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
    @attribute differentialOrder: The corresponding differential order, e.g. 2
  */
  variable : name=NAME (DIFFERENTIAL_ORDER)*;

  /**
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute calleeName: The (qualified) name of the functions
    @attribute args: Comma separated list of expressions representing parameters.
  */
  functionCall : calleeName=NAME LEFT_PAREN (expression (COMMA expression)*)? RIGHT_PAREN;

  /*********************************************************************************************************************
  * Equations-Language
  *********************************************************************************************************************/

  inlineExpression : (recordable=RECORDABLE_KEYWORD)? INLINE_KEYWORD variableName=NAME dataType EQUALS expression (SEMICOLON)?;

  odeEquation : lhs=variable EQUALS rhs=expression (SEMICOLON)?;

  kernel : KERNEL_KEYWORD variable EQUALS expression (COMMA variable EQUALS expression)* (SEMICOLON)?;

  /*********************************************************************************************************************
  * Procedural-Language
  *********************************************************************************************************************/

  block : ( stmt | NEWLINE )*;

  stmt : smallStmt | compoundStmt;

  compoundStmt : ifStmt
               | forStmt
               | whileStmt;

  smallStmt : assignment
            | functionCall
            | declaration
            | returnStmt;

  assignment : lhs_variable=variable
                (directAssignment=EQUALS |
                 compoundSum=PLUS_EQUALS |
                 compoundMinus=MINUS_EQUALS |
                 compoundProduct=STAR_EQUALS |
                 compoundQuotient=FORWARD_SLASH_EQUALS)
               expression;

  /** ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
   'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
    @attribute isRecordable: Is true iff. declaration is track-able.
    @attribute isFunction: Is true iff. declaration is a function.
    @attribute variable: List with variables.
    @attribute datatype: Obligatory data type, e.g., 'real' or 'mV/s'.
    @attribute sizeParameter: An optional array parameter, e.g., 'tau_syn ms[n_receptros]'.
    @attribute rhs: An optional initial expression, e.g., 'a real = 10+10'
    @attribute invariant: A single, optional invariant expression, e.g., '[a < 21]'
   */
  declaration :
    (isRecordable=RECORDABLE_KEYWORD)? (isFunction=FUNCTION_KEYWORD)?
    variable (COMMA variable)*
    dataType
    (LEFT_SQUARE_BRACKET sizeParameter=NAME RIGHT_SQUARE_BRACKET)?
    ( EQUALS rhs = expression)?
    (LEFT_LEFT_SQUARE invariant=expression RIGHT_RIGHT_SQUARE)?;

  /** ATReturnStmt Models the return statement in a function.
    @expression An optional return expression, e.g., return tempVar
   */
  returnStmt : RETURN_KEYWORD expression?;

  ifStmt : ifClause
            elifClause*
            (elseClause)?
            END_KEYWORD;

  ifClause : IF_KEYWORD expression COLON block;

  elifClause : ELIF_KEYWORD expression COLON block;

  elseClause : ELSE_KEYWORD COLON block;

  forStmt : FOR_KEYWORD var=NAME IN_KEYWORD start_from=expression ELLIPSIS end_at=expression STEP_KEYWORD
            (negative=MINUS?) (UNSIGNED_INTEGER | FLOAT)
            COLON
             block
            END_KEYWORD;

  whileStmt : WHILE_KEYWORD expression COLON block END_KEYWORD;

  /*********************************************************************************************************************
  * NestML-Language
  *********************************************************************************************************************/

  /** ASTNestMLCompilationUnit represents a collection of neurons as stored in a model.
    @attribute neuron: A list of processed models.
  */
  nestMLCompilationUnit: (neuron | NEWLINE )* EOF;

  /** ASTNeuron Represents a single neuron.
    @attribute Name:    The name of the neuron, e.g., ht_neuron.
    @attribute body:    The body of the neuron consisting of several sub-blocks.
  */
  neuron : NEURON_KEYWORD NAME body;

  /** ASTBody The body of the neuron, e.g. internal, state, parameter...
    @attribute blockWithVariables: A single block of variables, e.g. the state block.
    @attribute updateBlock: A single update block containing the dynamic behavior.
    @attribute equationsBlock: A block of ode declarations.
    @attribute inputBlock: A block of input buffer declarations.
    @attribute outputBlock: A block of output declarations.
    @attribute function: A block declaring a used-defined function.
  */
  body: COLON
         (NEWLINE | blockWithVariables | equationsBlock | inputBlock | outputBlock | updateBlock | function)*
         END_KEYWORD;

  /** ASTBlockWithVariables Represent a block with variables and constants, e.g.:
    state:
      y0, y1, y2, y3 mV [y1 > 0; y2 > 0]
    end

    @attribute state: True iff the varblock is a state.
    @attribute parameters:  True iff the varblock is a parameters block.
    @attribute internals: True iff the varblock is a state internals block.
    @attribute declaration: A list of corresponding declarations.
  */
  blockWithVariables:
    blockType=(STATE_KEYWORD | PARAMETERS_KEYWORD | INTERNALS_KEYWORD | INITIAL_VALUES_KEYWORD)
    COLON
      (declaration | NEWLINE)*
    END_KEYWORD;

  /** ASTUpdateBlock The definition of a block where the dynamical behavior of the neuron is stated:
      update:
        if r == 0: # not refractory
          integrate(V)
        end
      end
     @attribute block Implementation of the dynamics.
   */
  updateBlock: UPDATE_KEYWORD COLON
                block
                END_KEYWORD;

  /** ASTEquationsBlock A block declaring special functions:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (convolve(G, spikes) + I_e + I_stim)
       end
     @attribute inlineExpression: A single inline expression, e.g., inline V_m mV = ...
     @attribute odeEquation: A single ode equation statement, e.g., V_m' = ...
     @attribute kernel:      A single kernel statement, e.g., kernel V_m = ....
   */
  equationsBlock: EQUATIONS_KEYWORD COLON
                   (inlineExpression | odeEquation | kernel | NEWLINE)*
                   END_KEYWORD;

  /** ASTInputBlock represents a single input block, e.g.:
    input:
      spikeBuffer <- excitatory spike
      currentBuffer pA <- current
    end
    @attribute inputPort: A list of input ports.
  */
  inputBlock: INPUT_KEYWORD COLON
              (inputPort | NEWLINE)*
              END_KEYWORD;

  /** ASTInputPort represents a single input port, e.g.:
      spikeBuffer type <- excitatory spike
    @attribute name: The name of the input port.
    @attribute sizeParameter: Optional size parameter for multisynapse neuron.
    @attribute datatype: Optional data type of the buffer.
    @attribute inputQualifier: The qualifier keyword of the input port, to indicate e.g. inhibitory-only or excitatory-only spiking inputs on this port.
    @attribute isSpike: Indicates that this input port accepts spikes.
    @attribute isCurrent: Indicates that this input port accepts current generator input.
  */
  inputPort:
    name=NAME
    (LEFT_SQUARE_BRACKET sizeParameter=NAME RIGHT_SQUARE_BRACKET)?
    (dataType)?
    LEFT_ANGLE_MINUS inputQualifier*
    (isCurrent = CURRENT_KEYWORD | isSpike = SPIKE_KEYWORD);

  /** ASTInputQualifier represents the qualifier of an inputPort. Only valid for spiking inputs.
    @attribute isInhibitory: Indicates that this spiking input port is inhibitory.
    @attribute isExcitatory: Indicates that this spiking input port is excitatory.
  */
  inputQualifier : (isInhibitory=INHIBITORY_KEYWORD | isExcitatory=EXCITATORY_KEYWORD);

  /** ASTOutputBlock Represents the output block of the neuron,i.e., declarations of output buffers:
        output: spike
      @attribute isSpike: true iff the neuron has a spike output.
      @attribute isCurrent: true iff. the neuron is a current output.
    */
  outputBlock: OUTPUT_KEYWORD COLON (isSpike=SPIKE_KEYWORD | isCurrent=CURRENT_KEYWORD) ;

  /** ASTFunction A single declaration of a user-defined function definition:
      function set_V_m(v mV):
        y3 = v - E_L
      end
    @attribute name: The name of the function.
    @attribute parameters: List with function parameters.
    @attribute returnType: An arbitrary return type, e.g. String or mV.
    @attribute block: Implementation of the function.
  */
  function: FUNCTION_KEYWORD NAME LEFT_PAREN (parameter (COMMA parameter)*)? RIGHT_PAREN (returnType=dataType)?
           COLON
             block
           END_KEYWORD;

  /** ASTParameter represents a single parameter consisting of a name and the corresponding
      data type, e.g. T_in ms
    @attribute name: The name of the parameter.
    @attribute dataType: The corresponding data type.
  */
  parameter : NAME dataType;

