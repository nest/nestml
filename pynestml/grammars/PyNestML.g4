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

grammar PyNestML;

  options { tokenVocab = Tokens; }

  /*********************************************************************************************************************
  * Units-Language
  *********************************************************************************************************************/

  /**
    ASTDatatype. Represents predefined data types and gives a possibility to use an unit
    data type.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI data type
  */
  dataType : isInt='integer'
           | isReal='real'
           | isString='string'
           | isBool='boolean'
           | isVoid='void'
           | unit=unitType;
  /**
    ASTUnitType. Represents an unit data type. It can be a plain data type as 'mV' or a
    complex data type as 'mV/s'
  */
  unitType : leftParentheses='(' compoundUnit=unitType rightParentheses=')'
           | base=unitType powOp='**' exponent=INTEGER
           | left=unitType (timesOp='*' | divOp='/') right=unitType
           | unitlessLiteral=INTEGER divOp='/' right=unitType
           | unit=NAME;

  /*********************************************************************************************************************
  * Expressions-Language
  *********************************************************************************************************************/

  /**
   ASTExpression, i.e., several subexpressions combined by one or more operators,
   e.g., 10mV + V_m - (V_reset * 2)/ms, or a simple expression, e.g. 10mV.
  */
  expression : leftParentheses='(' term=expression rightParentheses=')'
         | <assoc=right> left=expression powOp='**' right=expression
         | unaryOperator term=expression
         | left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
         | left=expression (plusOp='+'  | minusOp='-') right=expression
         | left=expression bitOperator right=expression
         | left=expression comparisonOperator right=expression
         | logicalNot='not' term=expression
         | left=expression logicalOperator right=expression
         | condition=expression '?' ifTrue=expression ':' ifNot=expression
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
                   | (INTEGER|FLOAT) (variable)?
                   | string=STRING_LITERAL
                   | isInf='inf'
                   | variable;

  unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');

  bitOperator : (bitAnd='&'| bitXor='^' | bitOr='|' | bitShiftLeft='<<' | bitShiftRight='>>');

  comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');

  logicalOperator : (logicalAnd='and' | logicalOr='or' );

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
  functionCall : calleeName=NAME '(' (expression (',' expression)*)? ')';

  /*********************************************************************************************************************
  * Equations-Language
  *********************************************************************************************************************/

  odeFunction : (recordable='recordable')? 'function' variableName=NAME dataType '=' expression (';')?;

  odeEquation : lhs=variable '=' rhs=expression (';')?;

  odeShape : 'shape' lhs=variable '=' rhs=expression (';')?;

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
                (directAssignment='=' |
                 compoundSum='+='     |
                 compoundMinus='-='   |
                 compoundProduct='*=' |
                 compoundQuotient='/=')
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
    (isRecordable='recordable')? (isFunction='function')?
    variable (',' variable)*
    dataType
    ('[' sizeParameter=NAME ']')?
    ( '=' rhs = expression)?
    ('[[' invariant=expression ']]')?;

  /** ATReturnStmt Models the return statement in a function.
    @expression An optional return expression, e.g., return tempVar
   */
  returnStmt : 'return' expression?;

  ifStmt : ifClause
            elifClause*
            (elseClause)?
            BLOCK_CLOSE;

  ifClause : 'if' expression BLOCK_OPEN block;

  elifClause : 'elif' expression BLOCK_OPEN block;

  elseClause : 'else' BLOCK_OPEN block;

  forStmt : 'for' var=NAME 'in' start_from=expression '...' end_at=expression 'step'
            (negative='-'?) (INTEGER|FLOAT)
            BLOCK_OPEN
             block
            BLOCK_CLOSE;

  whileStmt : 'while' expression BLOCK_OPEN block BLOCK_CLOSE;

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
  neuron : 'neuron' NAME body;

  /** ASTBody The body of the neuron, e.g. internal, state, parameter...
    @attribute blockWithVariables: A single block of variables, e.g. the state block.
    @attribute updateBlock: A single update block containing the dynamic behavior.
    @attribute equationsBlock: A block of ode declarations.
    @attribute inputBlock: A block of input buffer declarations.
    @attribute outputBlock: A block of output declarations.
    @attribute function: A block declaring a used-defined function.
  */
  body: BLOCK_OPEN
         (NEWLINE | blockWithVariables | equationsBlock | inputBlock | outputBlock | updateBlock | function)*
         BLOCK_CLOSE;

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
    blockType=('state'|'parameters'|'internals'|'initial_values')
    BLOCK_OPEN
      (declaration | NEWLINE)*
    BLOCK_CLOSE;

  /** ASTUpdateBlock The definition of a block where the dynamical behavior of the neuron is stated:
      update:
        if r == 0: # not refractory
          integrate(V)
        end
      end
     @attribute block Implementation of the dynamics.
   */
  updateBlock: 'update' BLOCK_OPEN
                block
                BLOCK_CLOSE;

  /** ASTEquationsBlock A block declaring special functions:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (I_sum(G, spikes) + I_e + currents)
       end
     @attribute odeFunction: A single ode function statement, e.g., function V_m mV = ...
     @attribute odeEquation: A single ode equation statement, e.g., V_m' = ...
     @attribute odeShape:    A single ode shape statement, e.g., shape V_m = ....
   */
  equationsBlock: 'equations' BLOCK_OPEN
                   (odeFunction|odeEquation|odeShape|NEWLINE)*
                   BLOCK_CLOSE;

  /** ASTInputBlock represents a single input block:
    input:
      spikeBuffer   <- inhibitory excitatory spike
      currentBuffer <- current
    end
    @attribute inputLine: A list of input lines.
  */
  inputBlock: 'input' BLOCK_OPEN
              (inputLine | NEWLINE)*
              BLOCK_CLOSE;

  /** ASTInputLine represents a single line form the input, e.g.:
      spikeBuffer   <- inhibitory excitatory spike
    @attribute name:   The name of the defined buffer, inSpike.
    @attribute sizeParameter: Optional parameter representing  multisynapse neuron.
    @attribute datatype: Optional data type of the buffer.
    @attribute inputType: The type of the inputchannel: e.g. inhibitory or excitatory (or both).
    @attribute isSpike: True iff the neuron is a spike.
    @attribute isCurrent: True iff. the neuron is a current.
  */
  inputLine:
    name=NAME
    ('[' sizeParameter=NAME ']')?
    (dataType)?
    '<-' inputType*
    (isCurrent = 'current' | isSpike = 'spike');

  /** ASTInputType represents the type of the inputLine e.g.: inhibitory or excitatory:
    @attribute isInhibitory: true iff the neuron is a inhibitory.
    @attribute isExcitatory: true iff. the neuron is a excitatory.
  */
  inputType : (isInhibitory='inhibitory' | isExcitatory='excitatory');

  /** ASTOutputBlock Represents the output block of the neuron,i.e., declarations of output buffers:
        output: spike
      @attribute isSpike: true iff the neuron has a spike output.
      @attribute isCurrent: true iff. the neuron is a current output.
    */
  outputBlock: 'output' BLOCK_OPEN (isSpike='spike' | isCurrent='current') ;

  /** ASTFunction A single declaration of a user-defined function definition:
      function set_V_m(v mV):
        y3 = v - E_L
      end
    @attribute name: The name of the function.
    @attribute parameters: List with function parameters.
    @attribute returnType: An arbitrary return type, e.g. String or mV.
    @attribute block: Implementation of the function.
  */
  function: 'function' NAME '(' (parameter (',' parameter)*)? ')' (returnType=dataType)?
           BLOCK_OPEN
             block
           BLOCK_CLOSE;

  /** ASTParameter represents a single parameter consisting of a name and the corresponding
      data type, e.g. T_in ms
    @attribute name: The name of the parameter.
    @attribute dataType: The corresponding data type.
  */
  parameter : NAME dataType;

