<#--
  Generates C++ declaration
  @grammar: Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTDeclaration
  @param tc templatecontroller
  @result TODO
-->
${signature("variable")}
<#if variable.getDeclaringExpression().isPresent()>
  ${variable.getName()}_( ${tc.include("org.nest.spl.expr.Expr", variable.getDeclaringExpression().get())} )
<#else>
  ${variable.getName()}_()
</#if>
