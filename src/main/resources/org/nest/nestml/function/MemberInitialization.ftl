<#--
  Generates C++ declaration
  @grammar: Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTDeclaration
  @param tc templatecontroller
  @result TODO
-->

<#--  : C_      (250.0    ),  // pF-->
<#assign start="">

<#list ast.getDeclaration().getVars() as varname>
  <#if ast.getDeclaration().getExpr().isPresent()>
  ${start} ${varname}_( ${tc.include("org.nest.spl.expr.Expr", ast.getDeclaration().getExpr().get())} ) // NESTML type ${astNodes.computeTypeName(ast.getDeclaration().getDatatype())}
  <#else>
  ${start} ${varname}_() // NESTML type ${astNodes.computeTypeName(ast.getDeclaration().getDatatype())}
  </#if>
  <#assign start=",">
</#list>
