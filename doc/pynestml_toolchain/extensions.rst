Section 4: Extending PyNESTML 
------------------------------

As typical for all types of software, requirements of the implementation often change. PyNESTML was implemented with the aim to provide a modular and easy to extend framework which can be adjusted and reconfigured by exchanging components, e.g., context conditions and reference converters. In this section, we will briefly demonstrate how extensions to PyNESTML can be implemented. Representing components which are often adapted, the following use cases are introduced:

-  Grammar: How can the grammar artifacts be extended and in consequence which components have to be adapted?

-  Context Conditions: How can new semantical rules be introduced?

-  Code Generation: How can the code generator be extended?

All three scenarios represent use cases which often occur when new types of supported concepts are introduced.

Section 4.1: Modifying the Grammar 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following (hypothetical) use case illustrates the extension of the grammar: A new type of block shall be introduced. Declaring constraints which have to hold in each simulation step, this block contains boolean expressions representing invariants of the neuron model. It is therefore first necessary to extend PyNESTML's grammar to support a new type of blocks. :numref:`fig_new_grammar_rules` illustrates how a new grammar rule is introduced to support this use case.

.. _fig_new_grammar_rules:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_front_gram_cropped.jpg
   :alt: New grammar rules.

   New grammar rules: In order to include a new grammar rule, the existing *body* production is extended by a reference to the extension. The *invariantBlock* production encapsulates the added concept.

The grammar artifacts represent the starting point of each DSL. Consequently, all modification to the grammar have to be propagated to components which depend on its structure, namely:

-  The lexer and parser used to parse a model to a parse tree.

-  The AST classes storing details retrieved from the parse tree.

-  The base visitor as well as the *ASTBuilderVisitor* classes.

-  The symbol table building visitor as encapsulated in the *ASTSymbolTableVisitor*.

In :ref:`Section 1: The model-processing Frontend` we introduced how a manual implementation process of the lexer and parser can be avoided by utilizing Antlr. By executing Antlr on the modified grammar artifact, an implementation of the lexer and parser adapted to the extensions is generated. Together, these components are used to create the parse tree representation of a model. Proceeding, it is now necessary to provide a mutable data structure which is able to hold details retrieved from the parse tree. A new *ASTInvariantBlock* class is therefore implemented which holds all details of the new rule. As shown in :numref:`fig_new_grammar_rules`, each invariant block consists of a set of expressions. Consequently, the *ASTInvariantBlock* class features an attribute which stores lists of *ASTExpression* objects. Together with a set of data retrieval and modification operations, this class represents a data structure which is able to hold all invariants of a neuron model.

Having a modified metamodel, it remains to adapt PyNESTML to retrieve invariants from the parse tree. PyNESTML delegates the initialization of an AST to the *ASTBuilderVisitor* class, cf. :ref:`Section 1: The model-processing Frontend`. :numref:`fig_modifying_ast_builder` illustrates how the AST-building routine has to be adapted to regard the new *invariant* block. Here, it is also necessary to extend the existing *visitASTBody* rule to include the instantiation of *ASTInvariantBlock* nodes.

.. _fig_modifying_ast_builder:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_front_astB_cropped.jpg
   :alt: Modifying the AST builder.

   Modifying the AST builder: In order to initialize an AST according to the new grammar, the *ASTBuilderVisitor* is extended by an *ASTInvariantBlock*-node building method. An adaptation of the existing *visitASTBody* method includes the new rule.

With the modified structure of an AST where a new type of node has been added, it is also necessary to adapt the *ASTVistor* class. Implementing a basic traversal routine on the AST, here it is crucial to include an additional traversal method for the new type of AST node as well as the corresponding *visit* routine. Both methods can then be extended in concrete visitors in order to interact with the *invariant* block. As illustrated in :numref:`fig_modifying_ast_visitor`, all extensions are focused on a small set of methods. Besides a modification of the dispatcher methods, individual monomorphic functions are added.

.. _fig_modifying_ast_visitor:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_front_astVisitor_cropped.jpg
   :alt: Modifying the AST visitor.

   Modifying the AST visitor: The *ASTVisitor* class is adapted to support the new type of AST node. The dispatcher functions are adapted, while new monomorphic hook methods are added.

An initialized AST represents a base for further checks and modifications. :ref:`Section 1: The model-processing Frontend` illustrated how semantical checks are implemented by means of a symbol table and a set of context conditions. With a new type of block, it is, therefore, necessary to adapt the symbol table building routine. Extending the *ASTVisitor* class, all modifications are focused in the *ASTSymbolTableVisitor*. :numref:`fig_adapting_astsymboltablevisitor` illustrates how the symbol table construction routine has to be adapted.

.. _fig_adapting_astsymboltablevisitor:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_front_symbolVisitor_cropped.jpg
   :alt: Adapting the *ASTSymbolTableVisitor*.

   Adapting the *ASTSymbolTableVisitor*: The *traverseASTBody* method is extended to regard the new type of block, while the actual handling of the block is delegated to the *visitASTInvariantBlock* method.


Together, these steps enable PyNESTML to parse a model containing the new *invariant* block, construct the respective AST and populate the symbol table with all required details.

Section 4.2: Adding Context Conditions 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whenever a DSL is extended by new concepts, it also becomes necessary to regard additional semantic rules. In the case of the *invariant* block, it is essential to ensure that only boolean expressions have been stated in this type of block. With an initialized AST, this property can be easily checked by a new context condition. Whenever new semantic rules are established, it is therefore necessary to implement the following adaptations:

-  A new context condition implementing all required context checks.
-  A modification of the coordinating *CoCosManager* class.

In order to achieve modularity, each context condition is encapsulated in an individual class. The new *CoCoInvariantBlockCorrectlyTyped* class, therefore, implements all processes as required to check the handed over AST for correctness. Concrete checks are delegated to the *InvariantTypeCheckVisitor* class. Extending the *ASTVisitor*, this class implements a routine which visits the *ASTInvariantBlock* node of a given AST and iterates over all stated expressions. :ref:`Section 1: The model-processing Frontend` illustrated a preprocessing of the AST where the types of all expressions have been derived. It therefore only remains to check whether a boolean expression has been stated. :numref:`fig_adding_context_conditions` outlines how these modifications are implemented.

.. _fig_adding_context_conditions:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_front_context_cropped.jpg
   :alt: Adding context conditions.

   Adding context conditions: Each context condition is implemented in a self-contained class with all required functionality to check the context.


PyNESTML delegates the task of checking models for semantical correctness to the orchestrating *CoCosManager* class. Storing references to all implemented context conditions, this class encapsulates all implemented semantical checks. It is, therefore, necessary to extend this class by a reference to the above-introduced *CoCoInvariantBlockCorrectlyTyped*. Whenever a processed model is checked, all context conditions are consecutively invoked on the AST and errors are reported. :numref:`fig_extending_cocosmanager` illustrates how the *CoCosManager* class has to be extended to regard a new context condition.

.. _fig_extending_cocosmanager:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_front_cocos_cropped.jpg
   :alt: Extending the *CoCosManager*.

   Extending the *CoCosManager*: New context conditions have to be made known to the managing *CoCosManager* class.


Section 4.3: Modifying the code-generating Backend 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the introduction of new concepts to the model-processing frontend, it is also often intended to generate new artifacts or additional code. Extensions are hereby focused in the employed templates which depict how code has to be generated. In the case of the *invariant* block as introduced in the previous section, it is necessary to extend the existing set of templates to enable a generation of invariants in C++ code. The modularity of templates enables an easy to extend structure where additional concepts can be included by implementing sub-templates. Moreover, new templates can be composed of existing ones. Modifications to the code-generating backend are hereby conducted in the following components:

-  New templates which embody additional code that has to be generated.

-  The governing templates in order to include the extensions.

As illustrated in :numref:`fig_inclusion_new_templates`, the existing *NeuronClass* template is extended by a new *invariant* function which checks all stated invariants during the execution of the simulation. JinJa2 as the underlying generator engine of PyNESTML features concepts for template inclusion and therefore enables an easy extension of PyNESTML's code generator. The referenced template is hereby implemented as a new artifact.

.. _fig_inclusion_new_templates:

.. figure:: https://raw.githubusercontent.com/nest/NESTML/master/doc/pynestml_toolchain/pic/ext_back_temp_cropped.jpg
   :alt: Inclusion of new templates.

   Inclusion of new templates: The existing set of templates is modified to include additional templates. For the sake of modularity, each extension should be implemented in an individual artifact.


In conclusion, it is sufficient to implement all extensions in individual templates and include them by the above-demonstrated mechanism.

Back to :ref:`overview <PyNESTML - NESTML Toolchain in Python>`.
