<#--
  Generates C++ declaration
  @grammar:   FunctionCall = QualifiedName "(" ArgList ")";
              ArgList = (args:Expr ("," args:Expr)*)?;
  @param ast ASTFunctionCall
  @param tc templatecontroller
  @result TODO
-->
${expressionsPrinter.printMethodCall(ast)};

