# PyNestML - NestML Toolchain in Python

**Disclaimer**: This documentation represents PyNestML's implementation "as it is". **No guarantee of completeness or correctness is given.** As typical for all types of software, the actual implementation may change over time. The following documentation, therefore, provides an overview of the used components and approaches, while the actual code may be adapted in future. Nonetheless, the general ideas and concepts should remain applicable and valid.

Engineering of domain-specific languages (DSL) such as NestML represents a process which requires a fundamental understanding in two areas: The problem domain (e.g., computational neuroscience), and a set of tools to model and solve problems in this domain. In the following, we will leave all principles related to the former to the experts of the respective domain, and only demonstrate how the latter can be solved by means of a set of generated and hand-coded solutions. Consequently, no discussion of modeled aspects takes place, the language is therefore assumed to be given. Instead, we will demonstrate, starting from the specification of the language, which components are required and how these components have been implemented in PyNestML.

[Section 1](front.md) introduces the model processing frontend, a subsystem which is able to read in a (textual) model and instantiate a computer processable representation. [Section 2](middle.md) will subsequently demonstrate a set of assisting components which make interaction with the tool, as well as other tasks, easier to achieve. [Section 3](back.md) will then show how model-to-text transformations (i.e., code generation)  can be achieved. Finally, for those who are interested in extension points of PyNestML, [Sections 4](extensions.md) will subsume how the framework has to be adapted and extended to support new concepts in NestML.
  
<p align="center">
<img src="pic/dsl_archi_cropped.png" alt="The architecture of a DSL."
	width ="80%">
</p>
<a name="fig0.1"></a>
<p>
<b>Figure 0.1</b>: The architecture of a DSL<sup>[1](#1)</sup>: The model-processing toolchain consists of three major subsystems and several assisting components. A given model is handed over to the *model-processing frontend* which parses it and creates an internal representation, the *Abstract Syntax Tree* (AST). This representation is then further analyzed and refined by the *transformation and function library*, a collection of components which ensure the overall correctness of the given model and employ subroutines for further modifications and transformations, generating an *output AST*. The processed AST is finally handed over to the *backend* subsystem which generates code in a format as specified in a set of *templates*. The overall process is orchestrated by a *workflow execution* unit whose behavior and individual steps can be customized by a *control script*. The result of the overall process is a set of generated *code*, *reports* and other artifacts.
</p>


For more DSL-related details, we refer to Fow10<sup>[2](#2)</sup> and  Ben16<sup>[3](#3)</sup>.

---

<a name="1">[1]</a>: Katrin Hoelldobler, Bernhard Rumpe. MontiCore 5 Language Workbench Edition 2017. </a>

<a name="2">[2]</a>: Martin Fowler. Domain-specific languages. Pearson Education, 2010. </a>

<a name="3">[3]</a>: Benoit Combemale, Robert France and Jean-Marc Jezequel,  Bernhard Rumpe, James Steel and Didier Vojtisek. Engineering modeling languages: Turning domain knowledge into tools, 2016, CRC Press. </a>
