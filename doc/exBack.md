Modifying the code-generating Backend {#chap:ext:back}
=====================================

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
