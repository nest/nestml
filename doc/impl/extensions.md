## Section 4: Extending PyNestML {#chap:extension}

As typical for all types of software, requirements of the implementation
often change. PyNestML was implemented with the aim to provide a modular
and easy to extend framework which can be adjusted and reconfigured by
exchanging components, e.g., context conditions and reference
converters. In this chapter, we will briefly demonstrate how extensions
to PyNestML can be implemented. Representing components which are often
adapted, the following use cases are introduced:

-   Grammar: How can the grammar artifacts be extended and in
    consequence which components have to be adapted?

-   Context Conditions: How can new semantical rules be introduced?

-   Code Generation: How can the code generator be extended?

All three scenarios represent use cases which often occur when new types
of supported concepts are introduced.

### Section 4.1: Modifying the Grammar {#chap:ext:front}

The following (hypothetical) use case illustrates the extension of the
grammar: A new type of block shall be introduced. Declaring constraints
which have to hold in each simulation step, this block contains boolean
expressions representing invariants of the neuron model. It is therefore
first necessary to extend PyNestML’s grammar to support a new type of
blocks. illustrates how a new grammar rule is introduced to support this
use case.

![New grammar rules: In order to include a new grammar rule, the
existing *body* production is extended by a reference to the extension.
The *invariantBlock* production encapsulates the added concept.<span
data-label="ext:front:gram"></span>](src/pic/ext_front_gram_cropped.pdf){width="100.00000%"}

The grammar artifacts represent the starting point of each DSL.
Consequently, all modification to the grammar have to be propagated to
components which depend on its structure, namely:

-   The lexer and parser used to parse a model to a parse tree.

-   The AST classes storing details retrieved from the parse tree.

-   The base visitor as well as the *ASTBuilderVisitor* classes.

-   The symbol table building visitor as encapsulated in the
    *ASTSymbolTableVisitor*.

In we introduced how a manual implementation process of the lexer and
parser can be avoided by utilizing Antlr. By executing Antlr on the
modified grammar artifact, an implementation of the lexer and parser
adapted to the extensions is generated. Together, these components are
used to create the parse tree representation of a model. Proceeding, it
is now necessary to provide a mutable data structure which is able to
hold details retrieved from the parse tree. A new *ASTInvariantBlock*
class is therefore implemented which holds all details of the new rule.
As shown in , each invariant block consists of a set of expressions.
Consequently, the *ASTInvariantBlock* class features an attribute which
stores lists of *ASTExpression* objects. Together with a set of data
retrieval and modification operations, this class represents a data
structure which is able to hold all invariants of a neuron model.

Having a modified meta model, it remains to adapt PyNestML to retrieve
invariants from the parse tree. PyNestML delegates the initialization of
an AST to the *ASTBuilderVisitor* class, cf. . illustrates how the
AST-building routine has to be adapted to regard the new *invariant*
block. Here, it is also necessary to extend the existing *visitASTBody*
rule to include the instantiation of *ASTInvariantBlock* nodes.

![Modifying the AST builder: In order to initialize an AST according to
the new grammar, the *ASTBuilderVisitor* is extended by an
*ASTInvariantBlock* node building method. An adaptation of the existing
*visitASTBody* method includes the new rule.<span
data-label="ext:front:astB"></span>](src/pic/ext_front_astB_cropped.pdf){width="80.00000%"}

With the modified structure of an AST where a new type of node has been
added, it is also necessary to adapt the *ASTVistor* class. Implementing
a basic traversal routine on the AST, here it is crucial to include an
additional traversal method for the new type of AST node as well as the
corresponding visit routine. Both methods can then be extended in
concrete visitors in order to interact with the *invariant* block. As
illustrated in , all extensions are focused in a small set of methods.
Besides a modification of the dispatcher methods, individual monomorphic
functions are added.

![Modifying the AST visitor: The *ASTVisitor* class is adapted to
support the new type of AST node. The dispatcher functions are adapted,
while new monomorphic hook methods are added.<span
data-label="ext:front:astVisitor"></span>](src/pic/ext_front_astVisitor_cropped.pdf){width="80.00000%"}

An initialized AST represents a base for further checks and
modifications. Section \[chap:main:front:semantics\] illustrated how
semantical checks are implemented by means of a symbol table and a set
of context conditions. With a new type of block, it is therefore
necessary to adapt the symbol table building routine. Extending the
*ASTVisitor* class, all modifications are focused in the
*ASTSymbolTableVisitor*. illustrates how the symbol table construction
routine has to be adapted.

![Adapting the *ASTSymbolTableVisitor*: The *traverseASTBody* method is
extended to regard the new type of block, while the actual handling of
the block is delegated to the *visitASTInvariantBlock* method.<span
data-label="ext:front:symbolVisitor"></span>](src/pic/ext_front_symbolVisitor_cropped.pdf){width="70.00000%"}

Together, these steps enable PyNestML to parse a model containing the
new *invarinat* block, construct the respective AST and populate the
symbol table with all required details.

### Section 4.2: Modifying the code-generating Backend {#chap:ext:back}

With the introduction of new concepts to the model-processing frontend,
it is also often intended to generate new artifacts or additional code.
Extensions are hereby focused in the employed templates which depict how
code has to be generated. In the case of the *invariant* block as
introduced in the previous section, it is necessary to extend the
existing set of templates to enable a generation of invariants in C++
code. The modularity of templates enables an easy to extend structure
where additional concepts can be included by implementing sub-templates.
New templates can be composed of existing ones. Modifications to the
code-generating backend are hereby conducted in the following
components:

-   New templates which embody additional code that has to be generated.

-   The governing templates in order to include the extensions.

As illustrated in , the existing *NeuronClass* template is extended by a
new *invariant* function which checks all stated invariants during the
execution of the simulation. JinJa2 as the underlying generator engine
of PyNestML features concepts for template inclusion and therefore
enables an easy extension of PyNestML’s code generator. The referenced
template is hereby implemented as a new artifact.

![Inclusion of new templates: The existing set of templates is modified
to include additional templates. For the sake of modularity, each
extension should be implemented in an individual artifact.<span
data-label="ext:back:temp"></span>](src/pic/ext_back_temp_cropped.pdf){width="100.00000%"}

In conclusion, it is sufficient to implement all extensions in
individual templates and include them by the above-demonstrated
mechanism.

