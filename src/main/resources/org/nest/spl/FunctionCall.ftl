<#--
  Generates C++ declaration
  @grammar:   FunctionCall = QualifiedName "(" ArgList ")";
              ArgList = (args:Expr ("," args:Expr)*)?;
  @param ast ASTFunctionCall
  @param tc templatecontroller
  @result TODO
-->
<#if functions.isIntegrate(ast)>
${tc.include("org.nest.spl.ODEDeclaration", body.getEquations().get())}
<#else>
${expressionsPrinter.printMethodCall(ast)};
</#if>
