/*
 *  PyNESTML.g4
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


/**
  Grammar representing the Simple Programming Language (SPL). It is easy to learn imperative
  language which leans on the Python syntax.
*/
grammar PyNESTML;

  import Tokens;

  nestmlCompilationUnit : (neuron | NEWLINE )* EOF;
  /*********************************************************************************************************************
  * Units-Language
  *********************************************************************************************************************/

  /**
    ASTDatatype. Represents predefined datatypes and gives a possibility to use an unit
    datatype.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI datatype
  */
  datatype : isInt='integer'
           | isReal='real'
           | isString='string'
           | isBool='boolean'
           | isVoid='void'
           | unit=unitType;
  /**
    ASTUnitType. Represents an unit datatype. It can be a plain datatype as 'mV' or a
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
   ASTExpr, i.e., several subexpressions combined by one or more
   operators, e.g., 10mV + V_m - (V_reset * 2)/ms ....
   or a simple expression, e.g. 10mV.
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
  */
  simpleExpression : functionCall
                   | BOOLEAN_LITERAL // true & false;
                   | (INTEGER|FLOAT) (variable)?
                   | NAME
                   | isInf='inf'
                   | variable;

  unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');

  bitOperator : (bitAnd='&'| bitXor='^' | bitOr='|' | bitShiftLeft='<<' | bitShiftRight='>>');

  comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');

  logicalOperator : (logicalAnd='and' | logicalOr='or' );

  /**
    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    @attribute name
  */
  variable : NAME (differentialOrder)*;

  /**
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute name The (qualified) name of the fucntions
    @attribute args Comma separated list of expressions representing parameters.
  */
  functionCall : calleeName=NAME '(' (args=arguments)? ')';

  arguments : expression (',' expression)*;


  /*********************************************************************************************************************
  * Equations-Language
  *********************************************************************************************************************/

  odeFunction : (recordable='recordable')? 'function' variableName=NAME datatype '=' expression;

  odeEquation : lhs=derivative '=' rhs=expression;

  derivative : name=NAME (differentialOrder)*;

  differentialOrder: '\'';

  odeShape : 'shape' lhs=variable '=' rhs=expression;

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

  assignment : lhsVariable=variable
    (directAssignment='='       |
     compoundSum='+='     |
     compoundMinus='-='   |
     compoundProduct='*=' |
     compoundQuotient='/=') expression;


  /** ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
   'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
    @attribute hide is true iff. declaration is not trackable.
    @attribute function is true iff. declaration is an function.
    @attribute vars          List with variables
    @attribute Datatype      Obligatory data type, e.g. 'real' or 'mV/s'
    @attribute sizeParameter An optional array parameter. E.g. 'tau_syn ms[n_receptros]'
    @attribute expr An optional initial expression, e.g. 'a real = 10+10'
    @attribute invariants List with optional invariants.
   */
  declaration :
    isRecordable='recordable'? isFunction='function'?
    variable (',' variable)*
    datatype
    ('[' sizeParameter=NAME ']')?
    ( '=' rhs = expression)? SL_COMMENT?
    ('[[' invariant=expression ']]')?;

  /** ATReturnStmt Models the return statement in a function.

    @attribute minus An optional sing
    @attribute definingVariable Name of the variable
   */
  returnStmt : 'return' expression?;

  ifStmt : ifClause
            elifClause*
            (elseClause)?
            BLOCK_CLOSE;

  ifClause : 'if' expression BLOCK_OPEN block;

  elifClause : 'elif' expression BLOCK_OPEN block;

  elseClause : 'else' BLOCK_OPEN block;

  forStmt : 'for' var=NAME 'in' vrom=expression '...' to=expression 'step' step=signedNumericLiteral BLOCK_OPEN block BLOCK_CLOSE;

  whileStmt : 'while' expression BLOCK_OPEN block BLOCK_CLOSE;

  signedNumericLiteral : (negative='-') (INTEGER|FLOAT);

  /*********************************************************************************************************************
  * Nestml-Language
  *********************************************************************************************************************/
  /** ASTNeuron represents neuron.
    @attribute Name    The name of the neuron
    @attribute Body    The body of the neuron, e.g. internal, state, parameter...
  */
  neuron : 'neuron' NAME body;

  /** ASTBody The body of the neuron, e.g. internal, state, parameter...
  */
  body : BLOCK_OPEN
         (NEWLINE | blockWithVariables | updateBlock | equationsBlock | inputBlock | outputBlock | function)*
         BLOCK_CLOSE;

  /** ASTVar_Block represent a block with variables, e.g.:
    state:
      y0, y1, y2, y3 mV [y1 > 0; y2 > 0]
    end

    @attribute state true if the varblock ist a state.
    @attribute parameter true if the varblock ist a parameter.
    @attribute internal true if the varblock ist a state internal.
    @attribute AliasDecl a list with variable declarations.
  */
  blockWithVariables:
    blockType=('state'|'parameters'|'internals')
    BLOCK_OPEN
      (declaration | NEWLINE)*
    BLOCK_CLOSE;

  /** ASTDynamics a special function definition:
      update:
        if r == 0: # not refractory
          integrate(V)
        end
      end
     @attribute block Implementation of the dynamics.
   */
  updateBlock:
    'update'
    BLOCK_OPEN
      block
    BLOCK_CLOSE;

  /** ASTEquations a special function definition:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (I_sum(G, spikes) + I_e + currents)
       end
     @attribute odeDeclaration Block with equations and differential equations.
   */
  equationsBlock:
    'equations'
    BLOCK_OPEN
      (odeFunction|odeEquation|odeShape|NEWLINE)+
    BLOCK_CLOSE;

  /** ASTInput represents the input block:
    input:
      spikeBuffer   <- inhibitory excitatory spike
      currentBuffer <- current
    end

    @attribute inputLine set of input lines.
  */
  inputBlock: 'input'
    BLOCK_OPEN
      (inputLine | NEWLINE)*
    BLOCK_CLOSE;

  /** ASTInputLine represents a single line form the input, e.g.:
      spikeBuffer   <- inhibitory excitatory spike

    @attribute sizeParameter Optional parameter representing  multisynapse neuron.
    @attribute sizeParameter Type of the inputchannel: e.g. inhibitory or excitatory (or both).
    @attribute spike true iff the neuron is a spike.
    @attribute current true iff. the neuron is a current.
  */
  inputLine :
    name=NAME
    ('[' sizeParameter=NAME ']')?
    '<-' inputType*
    (isCurrent = 'current' | isSpike = 'spike');

  /** ASTInputType represents the type of the inputline e.g.: inhibitory or excitatory:
    @attribute inhibitory true iff the neuron is a inhibitory.
    @attribute excitatory true iff. the neuron is a excitatory.
  */
  inputType : (isInhibitory='inhibitory' | isExcitatory='excitatory');

  /** ASTOutput represents the output block of the neuron:
        output: spike
      @attribute spike true iff the neuron has a spike output.
      @attribute current true iff. the neuron is a current output.
    */
  outputBlock: 'output' BLOCK_OPEN (isSpike='spike' | isCurrent='current') ;

  /** ASTFunction a function definition:
      function set_V_m(v mV):
        y3 = v - E_L
      end
    @attribute name Functionname.
    @attribute parameters List with function parameters.
    @attribute returnType Complex return type, e.g. String
    @attribute primitiveType Primitive return type, e.g. int
    @attribute block Implementation of the function.
  */
  function: 'function' NAME '(' parameters? ')' (returnType=datatype)?
           BLOCK_OPEN
             block
           BLOCK_CLOSE;

  /** ASTParameters models parameter list in function declaration.
    @attribute parameters List with parameters.
  */
  parameters : parameter (',' parameter)*;

  /** ASTParameter represents singe:
      output: spike
    @attribute compartments Lists with compartments.
  */
  parameter : NAME datatype;