Extending PyNestML {#chap:extension}
==================

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
