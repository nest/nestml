<#--
  Generates C++ declaration
  @grammar: Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTDeclaration
  @param tc templatecontroller
  @result TODO
-->
<#assign declarationType = declarations.getDeclarationType(ast)>

<#list ast.getVars() as variableName>
${declarationType} ${variableName}_;
</#list>
